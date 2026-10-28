# FOSDEM 2026 · personal preparation pack

Platform engineer: operate a small self-hosted LLM service, from model artifacts and GPU sharing to serving reliability and AI-layer monitoring.

Display timezone: Europe/Madrid. Conference timezone: Europe/Brussels.
Historical FOSDEM 2026 replay with a synthetic attendee brief, not an attendance claim. Keep at most six sessions and use the gaps for notes, breaks and conversations. A 15-minute room-change allowance is a preference, not a measured route.

## Attendance and protected time

- 2026-01-31: 10:30–18:40 (Europe/Brussels)
- Lunch: 2026-01-31 12:30–13:15 (Europe/Brussels)

## Your agenda

### Sat 31 Jan · 11:00–11:20 | API Remoting for llama.cpp: Near-Native GPU Speed in macOS Containers
UD2.120 (Chavanne) · AI Plumbers · José Castillo Lema
[Official session](https://fosdem.org/2026/schedule/event/C9NF8K-api_remoting_for_llama_cpp_near-native_gpu_speed_in_macos_containers/)

Connects a local macOS development environment with Linux container tooling, a concrete deployment boundary for this attendee.

Questions:
- How do small-batch latency and sustained throughput change independently across the bridge?
- Which host and guest failure modes must an operator distinguish when acceleration stops?

Prepare: Bring a simple host-versus-container comparison matrix. Treat the near-native performance wording as the speaker's claim to examine, not an independently verified result.

Programme evidence: The latency overhead of API remoting versus the throughput gain from host GPU execution.

Notes:


### Sat 31 Jan · 13:55–14:15 | One GPU, Many Models: What Works and What Segfaults
UD2.120 (Chavanne) · AI Plumbers · YASH PANCHAL
[Official session](https://fosdem.org/2026/schedule/event/B39JSW-one-gpu-many-models/)

Directly addresses the shared-GPU utilization and failure-isolation decisions that make a small local serving setup difficult to operate.

Questions:
- Which failure modes affect only one model versus every tenant on the GPU?
- How should video-generation findings be validated before applying them to text inference?

Prepare: Write down GPU model, memory budget and concurrent workloads. Separate the speaker's video-generation setting from the attendee's LLM setting.

Programme evidence: MIG (hardware partitioning) and MPS (software sharing)

Notes:


### Sat 31 Jan · 15:40–16:00 | Supercharging LLM serving with Dynamo
UD2.120 (Chavanne) · AI Plumbers · Piotr Tarasiewicz
[Official session](https://fosdem.org/2026/schedule/event/Z7LBYT-supercharging_llm_serving_with_dynamo/)

Covers request routing, memory movement and fault tolerance, complementing the single-GPU case with a scale-out design.

Questions:
- At what workload size does disaggregation justify the extra operational components?
- What signals separate cache-routing benefits from extra transfer latency?

Prepare: Draw prefill, decode and KV-cache ownership on one page; capture which mechanisms matter for a small deployment versus a multi-node one.

Programme evidence: routes requests based on the KV cache hit rate and load

Notes:


### Sat 31 Jan · 16:05–16:25 | Taming the LLM Zoo with Docker Model Runner: Inference with OCI Artifacts, llama.cpp, and vLLM
UD2.120 (Chavanne) · AI Plumbers · Eric Curtin, Dorin Geman
[Official session](https://fosdem.org/2026/schedule/event/VGXWNS-taming_the_llm_zoo_with_docker_model_runner_inference_with_oci_artifacts_llama_c/)

Connects model artifacts, inference engines and a repeatable deployment lifecycle, directly matching the attendee's operational goal.

Questions:
- How are a model artifact and a compatible engine version pinned together?
- What rollback behavior is available when weights download correctly but fail at startup?

Prepare: Bring a model inventory with format, size, license and engine requirements. Ask which parts the OCI artifact actually captures.

Programme evidence: decoupling the model weights from the inference engine

Notes:


### Sat 31 Jan · 16:30–16:50 | From Infrastructure to Production: A Year of Self-Hosted LLMs
UD2.120 (Chavanne) · AI Plumbers · Mateusz Charytoniuk, Gosia Zagajewska, Luiz Miguel
[Official session](https://fosdem.org/2026/schedule/event/PD8WGF-from_infrastructure_to_production_a_year_of_self-hosted_llms/)

The mandatory session focuses on experience operating self-hosted LLMs and ties the architecture talks to day-to-day service ownership.

Questions:
- Which operational problem surprised you after the first deployment was already working?
- Which load-balancing or recovery pattern would you avoid for a small team?

Prepare: Prepare a failure log template covering symptoms, detection, mitigation and missing tooling. Do not treat a conference abstract as an incident dataset.

Programme evidence: What works, what doesn't, and what tooling we still need to build together.

Notes:


### Sat 31 Jan · 18:00–18:25 | AI Security Monitoring: Detecting Threats Against Production ML Systems
UB5.132 · Security · samuel desseaux
[Official session](https://fosdem.org/2026/schedule/event/ZXMKFM-ai_security_monitoring_detecting_threats_against_production_ml_systems/)

Completes the operations agenda with monitoring at the AI layer, beyond generic infrastructure dashboards.

Questions:
- Which proposed detections can be validated without logging sensitive prompts?
- How should false positives be assessed before connecting an alert to a response action?

Prepare: List model endpoints, trust boundaries and telemetry retention constraints. Capture candidate detection tests rather than assuming every advertised rule transfers.

Programme evidence: security-focused observability for production ML systems

Notes:


## Alternatives and tradeoffs

- [Containerization, the future](https://fosdem.org/2026/schedule/event/SEFQ3Q-containerization_the_future/) · Sat 31 Jan · 12:30–12:50 · UA2.118 (Henriot) · 4/5
  Overlaps Lunch. Relevant to the macOS container boundary, but it overlaps the protected lunch and is retained as an alternative.
- [Island: Sandboxing tool powered by Landlock](https://fosdem.org/2026/schedule/event/EW8M3R-island/) · Sat 31 Jan · 15:30–15:55 · UB5.132 · 4/5
  Time / room-change conflict. Conflicts with: Supercharging LLM serving with Dynamo, Taming the LLM Zoo with Docker Model Runner: Inference with OCI Artifacts, llama.cpp, and vLLM. A practical sandboxing option for local binaries; the room-change conflict with the higher-priority serving talk makes it an explicit alternative.
- [Multimodal support in llama.cpp - Achievements and Future Directions](https://fosdem.org/2026/schedule/event/LRZJEH-llama-cpp-multimodal/) · Sat 31 Jan · 10:35–10:55 · UD2.120 (Chavanne) · 3/5
  Lower total priority under session cap. Useful for understanding the local serving interface, but this brief prioritizes operating models over adding modalities.
- [The Perfect Open Source Toolkit for Container Monitoring](https://fosdem.org/2026/schedule/event/ABTDUF-the_perfect_open_source_toolkit_for_container_monitoring/) · Sat 31 Jan · 12:10–12:30 · UA2.118 (Henriot) · 3/5
  Lower total priority under session cap. Provides a baseline for container observability, although the AI-specific monitoring session is closer to the main goal.
- [OneAI: An Open-Source Framework for Managing AI Models at Scale](https://fosdem.org/2026/schedule/event/7PAYWS-oneai_an_open-source_framework_for_managing_ai_models_at_scale/) · Sat 31 Jan · 14:20–14:40 · UD2.120 (Chavanne) · 3/5
  Lower total priority under session cap. An infrastructure-oriented model lifecycle alternative, but its OpenNebula prerequisite adds adoption work for this small local serving brief.
- [Vulkan API for Machine Learning? Competing with CUDA and ROCm in llama.cpp](https://fosdem.org/2026/schedule/event/CZSPSC-llama-cpp-vulkan/) · Sat 31 Jan · 14:45–15:05 · UD2.120 (Chavanne) · 3/5
  Lower total priority under session cap. Useful for a mixed-vendor GPU fleet, but backend implementation detail is less urgent than service operations.
- [The Hidden Cost of Intelligence: The Energy Footprint of AI from Code to GPU Kernels](https://fosdem.org/2026/schedule/event/SPJDGF-energy-footprint-ai/) · Sat 31 Jan · 15:20–15:25 · UD2.120 (Chavanne) · 3/5
  Lower total priority under session cap. Adds an energy-measurement lens for a local service, but it is an optional deeper measurement topic under the six-session cap.
- [tract - an efficient rust neural network inference engine](https://fosdem.org/2026/schedule/event/YJJQTD-tract-and-torch-to-nnef/) · Sat 31 Jan · 11:25–11:45 · UD2.120 (Chavanne) · 2/5
  Below minimum relevance score. A useful lightweight-runtime alternative, but its embedded deployment focus is secondary to running a shared LLM service.
- [Review of kernel and user-space Neural Processing Unit (NPU) chips support on Linux](https://fosdem.org/2026/schedule/event/QGKD3P-review_of_kernel_and_user-space_neural_processing_unit_npu_chips_support_on_linu/) · Sat 31 Jan · 18:15–18:35 · UD2.120 (Chavanne) · 2/5
  Below minimum relevance score. Conflicts with: AI Security Monitoring: Detecting Threats Against Production ML Systems. A useful hardware-stack survey, but lower priority and incompatible with staying for the AI monitoring session.

## Review and remaining work

Reviewed the complete 71-track inventory, title indexes for AI Plumbers, Containers, Security, Python, Software Performance, Confidential Computing and HPC/Big Data. Sunday-only tracks fall outside this Saturday visit. Read the AI, container and security abstracts; prioritized serving operations over embedded accelerator development, cryptographic migration and application-specific workloads. Fifteen plausible sessions have individual preparation notes. Speaker performance and security claims were not independently tested.

Review the subjective choices and the live official programme before attending. Room availability, accessibility and actual travel times are not verified. This is a snapshot, not a live calendar subscription. Importing ICS is optional; repeated imports may duplicate events. HTML scratchpad notes are not saved.
