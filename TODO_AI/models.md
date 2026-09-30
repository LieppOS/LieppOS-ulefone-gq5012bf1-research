# Local LLM Model Candidates — GQ5012BF1 / LieppOS

Target device:

- **Ulefone Armor 29 Pro Thermal**
- **SoC:** MediaTek MT6878T / Dimensity 7400
- **CPU:** 4x Cortex-A78 + 4x Cortex-A55
- **GPU:** Mali-G615 MC2
- **NPU:** MediaTek NPU 655 / NeuroPilot
- **RAM:** 16 GB physical
- **Battery:** very large, suitable for sustained local inference
- **Goal:** maximize useful intelligence per watt, not merely run the largest model that fits

This document tracks the most promising local models for LieppOS and the intended benchmark order.

---

## 1. Recommended shortlist

| Model | Architecture / size | Best LieppOS role | Expected phone fit | Priority |
|---|---|---|---|---:|
| **LFM2.5-1.2B-Instruct** | 1.2B hybrid | always-on router / commands | Extremely light and fast | **P0** |
| **LFM2.5-8B-A1B** | ~8.3B total / ~1.5B active MoE | main fast assistant / agent | Excellent if runtime support is good | **P0** |
| **Ling-3.0-tiny** | ~7.9B total / ~1.3B active MoE | reasoning / tools / conversation | Excellent candidate for phone inference | **P0** |
| **Qwen3.5-4B** | 4B small general model | highest-quality small general assistant | Heavier than sparse MoE but still practical | **P0** |
| **Gemma 4 E2B** | compact multimodal model | image/audio/text assistant | Strong multimodal candidate | **P0** |
| **LFM2.5-2.6B** | 2.6B hybrid | lightweight conversational assistant | Very comfortable | P1 |
| **Phi-4-mini** | ~3.8B dense | reasoning baseline | Practical but likely less efficient | P1 |
| **SmolLM3-3B** | 3B | small baseline / comparison | Easy to run | P2 |

---

## 2. Model-by-model notes

### LFM2.5-1.2B-Instruct

**Intended role:** always-resident router and system-command model.

Use cases:

- intent classification
- command routing
- tool selection
- notification triage
- basic local Q&A
- deciding when a larger model is required

Example:

```text
"turn flashlight on"
"open thermal camera"
"battery percentage?"
"start max battery mode"
"which model should answer this?"
```

Why it is interesting:

- small enough to keep resident
- potentially excellent latency
- should have relatively low CPU/RAM requirements
- good candidate for battery-sensitive always-on use

Questions to benchmark:

- idle resident RAM
- first-token latency
- sustained tokens/s
- battery impact if kept loaded
- whether keeping it resident saves energy versus repeatedly loading larger models

**Priority:** P0

---

### LFM2.5-8B-A1B

**Intended role:** fast main LieppOS assistant.

Key attraction:

```text
~8B total capacity
      ↓
~1.5B active per token
```

This could provide much more model capacity than a dense ~1.5B model while retaining phone-friendly compute requirements.

Target use:

- tool calling
- multi-step commands
- conversational assistant
- structured output
- simple coding/help
- system automation

Direct comparison target:

```text
LFM2.5-8B-A1B
        VS
Ling-3.0-tiny
```

Benchmark specifically:

- decode speed
- prompt-processing speed
- RAM bandwidth pressure
- expert-routing overhead
- tokens/joule
- long-context degradation
- Vulkan compatibility
- NPU feasibility

**Priority:** P0

---

### Ling-3.0-tiny

**Intended role:** fast reasoning / agent model.

Approximate architecture:

- ~7.9B total parameters
- ~1.3B active parameters per token
- sparse Mixture-of-Experts

Why it suits the phone:

- compute behaves much closer to a small model than a dense 8B model
- total model capacity is still much larger than a conventional 1–2B model
- attractive balance for reasoning, conversation, coding and tool use

Expected useful quantization:

```text
Q4_K_M
```

Working assumption for the Armor 29 Pro Thermal:

- likely practical within 16 GB physical RAM
- likely fast enough for real-time streamed conversation
- 4K–8K context should be the initial target
- do not use huge context merely because the model supports it

Expected role:

```text
normal assistant
reasoning
coding
multi-step tools
automation
```

**Priority:** P0

---

### Qwen3.5-4B

**Intended role:** highest-quality small general model.

Why it matters:

- compact enough to remain practical on 16 GB RAM
- stronger general intelligence than most ultra-small models
- useful for reasoning, coding and agent tasks
- multimodal capability makes it relevant to camera/thermal workflows

Potential LieppOS examples:

```text
thermal image
    ↓
Qwen
    ↓
"this connector is significantly hotter than the surrounding board"
```

or:

```text
screenshot
    ↓
Qwen
    ↓
UI understanding + tool selection
```

Main downside:

- dense/small-model compute is likely more expensive per token than a 1.3–1.5B-active MoE
- may have worse tokens/joule than Ling/LFM A1B despite higher quality

Benchmark against:

```text
Ling-3.0-tiny
LFM2.5-8B-A1B
```

**Priority:** P0

---

### Gemma 4 E2B

**Intended role:** multimodal LieppOS assistant.

Target capabilities:

- text
- image
- audio
- function/tool calling
- local vision tasks

Especially relevant to this phone because LieppOS may eventually expose:

- thermal camera
- standard cameras
- uSmart cameras/accessories
- screenshots
- local speech input

Possible architecture:

```text
speech
camera
thermal image
screenshot
      ↓
Gemma 4 E2B
      ↓
LieppOS tool broker
```

Questions:

- actual Android runtime support
- image encoder memory cost
- audio pipeline cost
- decode speed
- whether multimodal inference remains usable under sustained thermal load

**Priority:** P0

---

### LFM2.5-2.6B

**Intended role:** medium-size lightweight chat baseline.

Useful as a comparison point between:

```text
1.2B always-on
     and
8B-A1B sparse assistant
```

Potentially a very clean choice if MoE memory access turns out inefficient on MT6878T.

**Priority:** P1

---

### Phi-4-mini

**Intended role:** reasoning baseline.

Useful because:

- conventional dense architecture
- good comparison against sparse/mobile-oriented alternatives
- helps determine whether architectural efficiency matters more than benchmark intelligence on this hardware

Measure:

- CPU speed
- Vulkan speed
- RAM
- power
- throttling

**Priority:** P1

---

### SmolLM3-3B

**Intended role:** lightweight open baseline.

Use mainly for:

- performance comparison
- runtime validation
- small-model energy testing
- fallback model if other architectures have backend compatibility issues

**Priority:** P2

---

## 3. Recommended LieppOS model stack

Do not use a single model for every task.

Proposed architecture:

```text
                   LieppOS AI
                       │
               tiny router model
               LFM2.5-1.2B
                       │
          ┌────────────┼─────────────┐
          │            │             │
       trivial      reasoning     multimodal
       commands        │             │
          │            │             │
          ▼            ▼             ▼
      local reply  Ling / LFM     Gemma 4
                   8B-A1B           E2B
                       │
                       │ quality escalation
                       ▼
                  Qwen3.5-4B
```

Target behavior:

```text
simple command
    -> 1.2B model only

normal conversation
    -> Ling or LFM2.5-8B-A1B

complex reasoning/coding
    -> Qwen3.5-4B

camera/audio task
    -> Gemma 4 E2B
```

The router should avoid waking or loading larger models unnecessarily.

---

## 4. Initial benchmark order

Benchmark on the actual Armor 29 Pro Thermal in this order:

1. LFM2.5-1.2B-Instruct
2. Ling-3.0-tiny Q4
3. LFM2.5-8B-A1B
4. Qwen3.5-4B Q4
5. Gemma 4 E2B
6. LFM2.5-2.6B
7. Phi-4-mini
8. SmolLM3-3B

For every model test:

### CPU backend

- optimized AArch64
- big-core affinity
- mixed A78/A55 affinity
- frequency scaling behavior

### GPU backend

- Vulkan / Mali-G615 MC2
- partial offload
- full supported offload
- GPU power and thermal behavior

### NPU backend

Where possible:

- NeuroPilot / Neuron
- TFLite
- ExecuTorch
- MediaTek-compatible runtime
- hybrid NPU + CPU

---

## 5. Mandatory benchmark metrics

For every model/backend/quantization combination record:

| Metric | Required |
|---|---|
| Model file size | YES |
| Quantization | YES |
| Physical RAM used | YES |
| KV-cache RAM | YES |
| Prompt-processing tok/s | YES |
| Decode tok/s | YES |
| Time to first token | YES |
| CPU utilization | YES |
| GPU utilization | YES |
| NPU utilization | YES if available |
| Device temperature | YES |
| Battery drain | YES |
| Approximate power draw | YES if measurable |
| Tokens/joule | **YES** |
| 5-minute sustained speed | YES |
| 15-minute sustained speed | YES |
| 30-minute sustained speed | YES |
| Throttling point | YES |
| Context length | YES |
| Android responsiveness during inference | YES |

The key LieppOS metric is:

```text
useful quality
      /
energy consumed
```

not maximum tokens/s alone.

---

## 6. Context policy

Initial context targets:

| Model class | Initial context target |
|---|---:|
| 1–2B router | 2K–4K |
| 3–4B assistant | 4K–8K |
| Sparse 8B-class assistant | 4K–8K |
| Heavy/manual mode | 8K–16K |

Avoid keeping huge context windows resident by default.

Prefer:

```text
short active context
        +
local memory database
        +
RAG / retrieval
```

instead of wasting RAM and memory bandwidth on 32K–128K context for ordinary phone use.

---

## 7. Quantization policy

Initial preferred quantization:

```text
Q4
```

Then compare:

```text
Q4
Q5
Q6
INT8 where accelerator support makes sense
```

Do not assume higher precision is better overall.

Evaluate:

```text
quality gain
    vs
RAM cost
    vs
speed loss
    vs
power cost
```

For always-on/local assistant use, Q4 is likely the first practical target.

---

## 8. Licensing / redistribution audit

Before bundling any model inside official LieppOS images, verify:

- redistribution rights
- commercial-use rights
- derivative-model rights
- quantized-weight redistribution
- attribution requirements
- acceptable-use clauses
- whether model files can be mirrored by LieppOS

Current shortlist should be categorized as:

```text
SAFE_TO_BUNDLE
BUNDLE_WITH_ATTRIBUTION
USER_DOWNLOAD_REQUIRED
REVIEW_REQUIRED
```

Do not ship weights automatically until the exact current license for that model/version has been reviewed.

---

## 9. Model-selection goals

The final benchmark should select at least:

### Best always-on model

Target:

- minimal idle RAM
- extremely low latency
- extremely low power
- reliable tool routing

Likely candidate:

```text
LFM2.5-1.2B
```

### Best fast assistant

Target:

- strong conversation
- tool use
- > acceptable sustained decode speed
- good tokens/joule

Likely candidates:

```text
Ling-3.0-tiny
LFM2.5-8B-A1B
```

### Best quality small model

Likely candidate:

```text
Qwen3.5-4B
```

### Best multimodal model

Likely candidate:

```text
Gemma 4 E2B
```

---

## 10. Open questions

- Does sparse MoE inference actually outperform dense 3–4B models on the MT6878T memory subsystem?
- Is Ling-3.0-tiny faster than LFM2.5-8B-A1B on ARM CPU?
- Which model gives the best tokens/joule?
- Does Mali Vulkan improve speed enough to justify its power draw?
- Can NPU 655 accelerate any of these architectures substantially?
- Can NPU 655 execute MoE routing and expert GEMMs efficiently?
- What is the best 24/7 resident model?
- Does a tiny router + larger on-demand model save energy versus one medium model always loaded?
- What is the practical RAM ceiling while keeping Android responsive?
- What context length produces the best user experience per watt?
- Which model produces the most reliable structured tool calls?
- Which model is best at Lithuanian and multilingual use?
- Which model best understands thermal-camera imagery after the LieppOS vision pipeline is implemented?

---

## 11. Initial recommendation

First serious comparison:

```text
LFM2.5-1.2B
      ↓
always-on baseline

Ling-3.0-tiny
      VS
LFM2.5-8B-A1B
      ↓
fast serious assistant

Qwen3.5-4B
      ↓
quality benchmark

Gemma 4 E2B
      ↓
multimodal benchmark
```

Do not decide the default model based on desktop benchmark tables.

The default LieppOS model must be chosen using **real measurements on the GQ5012BF1**.
