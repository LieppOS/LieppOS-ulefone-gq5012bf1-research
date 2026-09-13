// SPDX-License-Identifier: GPL-2.0
/*
 * Secure-call dispatcher for tkcore_drv: one CPU-bound kthread per possible
 * CPU, a single global request queue and a single global mutex that serialises
 * every entry into the secure world.
 *
 * Reconstructed from stock tkcore_drv.ko:
 *   tee_init_task      .text 0x2384   tee_exit_task   .text 0x263c
 *   run_tee_task       .text 0x1f30   tkcore_smc_task .text 0x294c
 *   do_smc             .text 0x26c4   tee_cpu_online  .text 0x2b28
 *   tee_cpu_prepare_down .text 0x2b34
 *   default_affinity_operations      .rodata 0x0c8
 *   tee_bind_cpu_request_operations  .rodata 0x290
 *
 * Nothing about the secure world itself is modelled here: the thread only
 * hands the register block to ptee->invoke_tee() and re-enters on the stock
 * "preempted by foreign interrupt" return value.
 */
#define pr_fmt(fmt) "tkcore_drv: " fmt

#include <linux/completion.h>
#include <linux/cpu.h>
#include <linux/delay.h>
#include <linux/cpumask.h>
#include <linux/kthread.h>
#include <linux/ktime.h>
#include <linux/list.h>
#include <linux/module.h>
#include <linux/mutex.h>
#include <linux/sched.h>
#include <linux/slab.h>
#include <linux/spinlock.h>
#include <linux/wait.h>

#include "tkcore_drv.h"

/* Stock caps the thread array at NR_CPUS = 32 (printk "nr_cpus %d exceeds NR_CPUS %d"). */
#define TKCORE_MAX_CPUS		32

/* run_tee_task() gives up trying to online a CPU after ~2 ms. */
#define TKCORE_BIND_TIMEOUT_US	2000

static struct tee_task_ctl tee_task_ctl;
static int nr_cpus __read_mostly;

/*
 * Default policy: never bind a call to a particular CPU.  The stock table is
 * three no-ops returning false/true/0 (.rodata+0xc8).
 */
static bool default_affinity_need_bind_cpu(void *arg)
{
	return false;
}

static bool default_affinity_match_cpu(void *arg, int cpu)
{
	return true;
}

static int default_affinity_get_candidate_cpu(void *arg)
{
	return 0;
}

const struct tee_affinity_ops default_affinity_operations = {
	.need_bind_cpu = default_affinity_need_bind_cpu,
	.match_cpu = default_affinity_match_cpu,
	.get_candidate_cpu = default_affinity_get_candidate_cpu,
};

/*
 * Secure-world requested policy: the secure OS asked for a specific CPU (the
 * requested mask/id arrives in the RPC argument).  Stock bodies:
 *   need_bind_cpu  -> mov w0,#1 ; ret
 *   match_cpu      -> cmp arg,cpu -> eq
 *   get_candidate_cpu -> return arg
 */
static bool tee_bind_cpu_request_need_bind_cpu(void *arg)
{
	return true;
}

static bool tee_bind_cpu_request_match_cpu(void *arg, int cpu)
{
	return (int)(uintptr_t)arg == cpu;
}

static int tee_bind_cpu_request_get_candidate_cpu(void *arg)
{
	return (int)(uintptr_t)arg;
}

const struct tee_affinity_ops tee_bind_cpu_request_operations = {
	.need_bind_cpu = tee_bind_cpu_request_need_bind_cpu,
	.match_cpu = tee_bind_cpu_request_match_cpu,
	.get_candidate_cpu = tee_bind_cpu_request_get_candidate_cpu,
};

/**
 * do_smc() - enter the secure world once, then absorb IRQ preemptions
 *
 * Every secure entry in the driver funnels through here while holding the
 * global mutex, so the secure world sees exactly one normal-world caller at a
 * time.  When the monitor returns TKCORE_SMC_RETURN_RPC_IRQ the call is simply
 * resumed with RETURN_FROM_RPC, preserving the SMC32/SMC64 bit of the original
 * function id (stock: (a0 & 0x80000000) | 0x72000003).
 */
static void do_smc(struct tee_tz *ptee, struct smc_param *param,
		   struct smc_param *out)
{
	struct tee_task_ctl *ctl = &tee_task_ctl;
	u64 first_a0 = param->a0;
	ktime_t start, end;
	s64 duration_us;
	int ret;

	mutex_lock(&ctl->g_lock);

	out->a0 = param->a0;
	out->a1 = param->a1;

	start = ktime_get();
	ret = ptee->invoke_tee(ptee, (u32)param->a0, param->a1, param->a2,
			       param->a3, param);
	end = ktime_get();
	if (ret) {
		pr_err("Unexpected invoke tee failed with %d\n", ret);
		param->a0 = ret;
		goto out_unlock;
	}

	duration_us = ktime_to_us(end) - ktime_to_us(start);
	if (duration_us > TKCORE_SMC_WARN_DURATION_US)
		pr_warn("WARNING SMC[0x%x] %sDURATION %lld us\n",
			(u16)param->a0,
			((u16)param->a0 == TKCORE_RPC_FUNC_IRQ + 1) ? "IRQ " : "",
			duration_us);
	if (duration_us > ctl->max_duration_us)
		ctl->max_duration_us = duration_us;

	while ((u32)param->a0 == TKCORE_SMC_RETURN_RPC_IRQ) {
		param->a0 = (first_a0 & TKCORE_SMC_32_64_MASK) |
			    (TKCORE_SMC_STD_CALL_PREFIX |
			     TKCORE_SMC_FUNC_RETURN_FROM_RPC);
		out->a0 = param->a0;
		out->a1 = param->a1;

		start = ktime_get();
		ret = ptee->invoke_tee(ptee, (u32)param->a0, param->a1,
				       param->a2, param->a3, param);
		end = ktime_get();
		if (ret) {
			pr_err("Unexpected invoke tee failed with %d\n", ret);
			param->a0 = ret;
			break;
		}

		duration_us = ktime_to_us(end) - ktime_to_us(start);
		if (duration_us > TKCORE_SMC_WARN_DURATION_US)
			pr_warn("WARNING SMC[0x%x] %sDURATION %lld us\n",
				(u16)param->a0,
				((u16)param->a0 == TKCORE_RPC_FUNC_IRQ + 1) ?
					"IRQ " : "",
				duration_us);
		if (duration_us > ctl->max_duration_us)
			ctl->max_duration_us = duration_us;
	}

out_unlock:
	mutex_unlock(&ctl->g_lock);
}

/**
 * tkcore_smc_task() - per-CPU secure call worker (stock name tkcore_smc_task.N)
 */
static int tkcore_smc_task(void *arg)
{
	struct tee_task_ctl *ctl = &tee_task_ctl;
	int cpu = (int)(long)arg;
	struct tee_task_req *req;
	DEFINE_WAIT(wait);

	if (cpu < 0 || cpu >= nr_cpus) {
		pr_err("bad cpu: %d\n", cpu);
		return 0;
	}

	while (!kthread_should_stop()) {
		spin_lock(&ctl->q_lock);
		for (;;) {
			prepare_to_wait(&ctl->threads[cpu].thread_wq, &wait,
					TASK_INTERRUPTIBLE);
			if (!list_empty(&ctl->queue)) {
				req = list_first_entry(&ctl->queue,
						       struct tee_task_req,
						       node);
				list_del(&req->node);
				break;
			}
			smp_mb();
			ctl->idle_mask &= ~(1u << cpu);
			spin_unlock(&ctl->q_lock);
			schedule();
			spin_lock(&ctl->q_lock);
			finish_wait(&ctl->threads[cpu].thread_wq, &wait);
		}
		finish_wait(&ctl->threads[cpu].thread_wq, &wait);
		spin_unlock(&ctl->q_lock);

		do_smc(req->ptee, req->param, req->out);
		complete(&req->done);
	}

	return 0;
}

static int tee_cpu_online(unsigned int cpu)
{
	return 0;
}

static int tee_cpu_prepare_down(unsigned int cpu)
{
	struct tee_task_ctl *ctl = &tee_task_ctl;

	if (cpu >= (unsigned int)nr_cpus) {
		pr_err("Bad cpu: %d\n", cpu);
		return -1;
	}

	/* Refuse to take the CPU down while its worker owns a secure call. */
	if (ctl->idle_mask & (1u << cpu))
		return -1;

	kthread_bind(ctl->threads[cpu].task, cpu);

	return 0;
}

int tee_init_task(void)
{
	struct tee_task_ctl *ctl = &tee_task_ctl;
	struct task_struct *task;
	int cpu;
	int ret;

	mutex_init(&ctl->g_lock);
	ctl->waiters = 0;
	init_completion(&ctl->wait_done);
	ctl->max_duration_us = 0;
	ctl->reserved90 = 0;

	nr_cpus = bitmap_weight(cpumask_bits(cpu_possible_mask), nr_cpu_ids);
	if (nr_cpus > TKCORE_MAX_CPUS) {
		pr_err("nr_cpus %d exceeds NR_CPUS %d\n", nr_cpus,
		       TKCORE_MAX_CPUS);
		return -1;
	}

	ctl->idle_mask = 0;
	INIT_LIST_HEAD(&ctl->queue);
	spin_lock_init(&ctl->q_lock);
	ctl->cpuhp_state = 0;
	ctl->nr_threads = nr_cpus;

	ctl->threads = kmalloc_array(nr_cpus, sizeof(*ctl->threads),
				     GFP_KERNEL);
	if (!ctl->threads) {
		pr_err("bad kmalloc %zu bytes for threads\n",
		       (size_t)nr_cpus * sizeof(*ctl->threads));
		return -ENOMEM;
	}

	for_each_possible_cpu(cpu) {
		if (cpu >= nr_cpus)
			break;
		init_waitqueue_head(&ctl->threads[cpu].thread_wq);
		task = kthread_create_on_node(tkcore_smc_task,
					      (void *)(long)cpu, NUMA_NO_NODE,
					      "tkcore_smc_task.%u", cpu);
		if (IS_ERR(task)) {
			pr_err("failed to start tkcore_smc_task.%d: %p\n",
			       cpu, task);
			ret = -1;
			goto err_threads;
		}
		ctl->threads[cpu].task = task;
		kthread_bind(task, cpu);
	}

	for (cpu = 0; cpu < ctl->nr_threads; cpu++)
		wake_up_process(ctl->threads[cpu].task);

	ret = cpuhp_setup_state_nocalls(CPUHP_AP_ONLINE_DYN,
					"tee/tkcore_tzdrv:cpu_listener",
					tee_cpu_online, tee_cpu_prepare_down);
	if (ret < 0)
		goto err_threads;

	ctl->cpuhp_state = ret;

	return 0;

err_threads:
	if (ctl->threads) {
		for (cpu = 0; cpu < ctl->nr_threads; cpu++) {
			if (IS_ERR_OR_NULL(ctl->threads[cpu].task))
				break;
			kthread_stop(ctl->threads[cpu].task);
		}
		kfree(ctl->threads);
		ctl->threads = NULL;
	}

	return ret;
}

void tee_exit_task(void)
{
	struct tee_task_ctl *ctl = &tee_task_ctl;
	int cpu;

	cpuhp_remove_state_nocalls(ctl->cpuhp_state);

	for (cpu = 0; cpu < ctl->nr_threads; cpu++)
		kthread_stop(ctl->threads[cpu].task);

	kfree(ctl->threads);
	ctl->threads = NULL;
}

/**
 * run_tee_task() - execute one secure call, honouring the CPU binding policy
 *
 * If the active policy does not require a specific CPU the call is made inline
 * on the caller's CPU.  Otherwise the request is queued and a CPU-bound worker
 * performs it; when no acceptable CPU is online the stock code asks the
 * hotplug core to bring the candidate up (add_cpu()) and retries for ~2 ms.
 *
 * Special secure-world returns are handled here, not by the caller:
 *   TKCORE_SMC_RETURN_BIND_CPU / TKCORE_SMC_RETURN_RPC_BIND_CPU
 *        - switch to the requested-CPU policy and resume the call
 *   TKCORE_SMC_RETURN_BUSY
 *        - park on the global completion until another call releases it
 */
void run_tee_task(struct tee_tz *ptee, struct smc_param *param,
		  struct tee_affinity *aff)
{
	struct tee_task_ctl *ctl = &tee_task_ctl;
	u64 first_a0 = param->a0;
	u64 rpc_resume = (first_a0 & TKCORE_SMC_32_64_MASK) |
			 (TKCORE_SMC_STD_CALL_PREFIX |
			  TKCORE_SMC_FUNC_RETURN_FROM_RPC);
	struct smc_param out = { 0 };
	struct tee_task_req req;
	ktime_t start;
	bool need_wake;
	int cpu;
	int ret;

	for (;;) {
		if (aff->ops->need_bind_cpu(aff->arg)) {
			init_completion(&req.done);
			req.ptee = ptee;
			req.param = param;
			req.out = &out;
			INIT_LIST_HEAD(&req.node);

			start = ktime_get();
			need_wake = false;
			cpu = -1;

			for (;;) {
				int c;

				cpus_read_lock();
				spin_lock(&ctl->q_lock);

				cpu = -1;
				if (ctl->idle_mask) {
					for (c = 0; c < nr_cpus; c++) {
						if (ctl->idle_mask & (1u << c)) {
							cpu = c;
							need_wake = false;
							goto queue;
						}
					}
				}

				for_each_online_cpu(c) {
					if (aff->ops->match_cpu(aff->arg, c)) {
						cpu = c;
						break;
					}
				}

				if (cpu >= 0) {
					ctl->idle_mask |= 1u << cpu;
					smp_mb();
					need_wake = true;
				}
queue:
				cpus_read_unlock();
				if (cpu >= 0)
					list_add_tail(&req.node, &ctl->queue);
				spin_unlock(&ctl->q_lock);

				if (cpu >= 0)
					break;

				if (ktime_to_us(ktime_get()) -
				    ktime_to_us(start) >= TKCORE_BIND_TIMEOUT_US) {
					need_wake = false;
					break;
				}

				c = aff->ops->get_candidate_cpu(aff->arg);
				ret = add_cpu(c);
				if (ret)
					pr_err("tkcore: cpu_on(%d) failed with ret: %d\n",
					       c, ret);
				usleep_range(50, 100);
			}

			if (cpu < 0) {
				/* Nobody could take it: run it here instead. */
				do_smc(ptee, param, &out);
			} else {
				if (need_wake)
					wake_up(&ctl->threads[cpu].thread_wq);
				wait_for_completion(&req.done);
			}
		} else {
			do_smc(ptee, param, &out);
		}

		switch ((u32)param->a0) {
		case TKCORE_SMC_RETURN_BIND_CPU:
			aff->ops = &tee_bind_cpu_request_operations;
			aff->arg = (void *)(uintptr_t)(u32)param->a1;
			param->a0 = out.a0;
			param->a1 = out.a1;
			continue;
		case TKCORE_SMC_RETURN_RPC_BIND_CPU:
			aff->ops = &tee_bind_cpu_request_operations;
			aff->arg = (void *)(uintptr_t)(u32)param->a1;
			param->a0 = rpc_resume;
			param->a1 = 0;
			continue;
		case TKCORE_SMC_RETURN_BUSY:
			ctl->waiters++;
			wait_for_completion(&ctl->wait_done);
			param->a0 = first_a0;
			continue;
		default:
			break;
		}

		if (TKCORE_SMC_RETURN_IS_RPC(param->a0)) {
			if (ctl->waiters > 0) {
				ctl->waiters--;
				complete(&ctl->wait_done);
			}
		}
		return;
	}
}
