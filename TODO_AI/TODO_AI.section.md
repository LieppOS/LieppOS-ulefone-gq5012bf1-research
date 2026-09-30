## Local AI / On-Device LLM

**Goal:** make the Armor 29 Pro Thermal a first-class offline AI device under LieppOS, optimized for useful tokens-per-joule rather than only peak benchmark speed.

### Hardware baseline

- SoC: MediaTek MT6878T / Dimensity 7400
- CPU: 4x Cortex-A78 + 4x Cortex-A55
- GPU: Mali-G615 MC2
- NPU: MediaTek NPU 655 / NeuroPilot generation
- RAM: 16 GB physical
- Large battery and unusually substantial cooling make sustained local inference more realistic than on a typical midrange phone.

### Model-size targets

| Model class | Target role | Priority |
|---|---|---:|
| 1–2B Q4 | always-available command/router model | HIGH |
| 3–4B Q4 | default local assistant | HIGH |
| 7–8B Q4 | high-quality local chat/reasoning | HIGH |
| 12–14B Q4 | optional heavy local model | MEDIUM |
| 20B+ | research only; likely poor UX / memory pressure | LOW |

Do **not** count Android "RAM expansion" / swap-backed virtual RAM as real model capacity.

### Runtime investigation

Benchmark and compare:

1. `llama.cpp` CPU-only AArch64
2. `llama.cpp` / compatible Vulkan backend on Mali-G615
3. MLC / Vulkan where useful
4. ExecuTorch/TFLite paths
5. MediaTek NeuroPilot / NPU 655 if usable
6. hybrid CPU + GPU/NPU execution if supported

For each backend record:

- prompt processing tokens/s
- decode tokens/s
- first-token latency
- total RAM
- model RAM
- KV-cache RAM
- CPU/GPU/NPU utilization
- average package power if measurable
- battery drain per hour
- device temperature
- throttling behavior
- sustained 5/15/30-minute performance
- tokens per joule

### NPU 655 / NeuroPilot research

Determine exactly what the stock system provides for the MT6878T NPU:

- kernel drivers
- device nodes
- firmware
- APU/NPU DT nodes
- reserved memory
- IOMMU paths
- power domains
- clocks
- vendor HAL/services
- NeuroPilot/Neuron runtime libraries
- model compiler/converter dependencies
- supported tensor formats
- supported precisions: INT8 / INT16 / FP16 / others
- Android NNAPI / TFLite / ExecuTorch integration
- whether an LLM graph can execute substantially on NPU 655
- whether proprietary userspace/firmware remains mandatory even with an open kernel

Search stock vendor/system for at least:

`neuron`
`neuropilot`
`apu`
`mdla`
`npu`
`vpu`
`nnapi`
`mtk_nn`
`libneuron`
`libapu`
`executorch`
`tflite`

Create research under:

```text
ai/
├── README.md
├── npu655-stock-stack.md
├── npu655-kernel-contract.md
├── npu655-userspace-runtime.md
├── npu655-open-source-gap.md
├── llama-cpp-arm64.md
├── mali-vulkan-llm.md
├── model-memory-budget.md
├── benchmark-methodology.md
└── benchmark-results.tsv
```

### Kernel / LieppOS power policy

Create an AI-specific power profile rather than pinning everything at maximum clocks.

Desired behavior:

```text
AI idle
  -> NPU/GPU runtime suspended
  -> CPU normal battery policy

small-model inference
  -> prefer efficient CPU configuration
  -> minimal DRAM/interconnect vote

heavy inference
  -> enable only required A78 cores
  -> enable GPU/NPU when beneficial
  -> raise memory bandwidth only as required

generation stops
  -> immediate DVFS decay
  -> GPU/NPU runtime suspend
  -> deep idle restored
```

Investigate:

- CPU affinity by model/backend
- uclamp
- scheduler placement
- CPU frequency sweet spots
- GPU DVFS sweet spots
- NPU DVFS / power gating
- memory/interconnect bandwidth votes
- thermal throttling thresholds
- runtime PM latency
- cost of keeping accelerator domains awake

Do not globally disable thermal protection or force unsafe clocks/voltages.

### LieppOS local-assistant architecture

Long-term target:

```text
Local LLM
   |
   +-- speech
   +-- vision
   +-- LieppOS privileged broker
   +-- Android 17 AppFunctions / equivalent controlled APIs
   |
   +-- thermal camera
   +-- uSmart accessories
   +-- cameras
   +-- battery/power state
   +-- system settings
   +-- user-approved automation
```

Do **not** give the model unrestricted root access. Use a narrow privileged broker with explicit capabilities, user authorization, audit logging and per-action policy.

### Multi-model strategy

Prefer several models instead of keeping one large model resident:

```text
1–2B  -> routing / commands / classification
3–4B  -> normal assistant
7–8B  -> complex reasoning / conversation
12–14B -> explicit "Heavy Local AI" mode
```

Investigate fast model unload/reload and whether a tiny resident router materially reduces total energy use.

### Initial success criteria

The first useful milestone is:

- fully offline
- 7–8B Q4 model loads without Android memory instability
- sustained conversational decode speed
- no severe thermal throttling over 30 minutes
- screen-off/idle power returns to normal after inference
- no accelerator domain remains accidentally awake
- repeatable benchmark suite
- CPU vs Vulkan vs NPU comparison
- measured tokens-per-joule
- clear recommendation for LieppOS default backend/model

### Open questions

- Can NPU 655 efficiently execute transformer decode, or only selected graph operators?
- Does the stock NeuroPilot stack expose enough interfaces for third-party LLM execution?
- Can the NPU stack be retained as proprietary userspace while the kernel side becomes source-built?
- Is Mali Vulkan faster and/or more efficient than optimized A78 CPU inference on this exact device?
- What CPU/GPU/NPU frequency point gives the best tokens-per-joule?
- What is the largest practical model with 16 GB physical RAM while keeping Android responsive?
- How much context can 7–8B and 12–14B models sustain before KV-cache pressure becomes unacceptable?
- Can Android 17 AppFunctions be used with a completely local LieppOS model without dependence on Google AI services?
