# Deep Research Prompt D: Local LLM Inference, Prompt Optimization, and Experimental Methodology for Omics Metadata Harmonization

---

## PREAMBLE AND INSTRUCTIONS TO THE RESEARCH AGENT

You are a senior ML engineer and experimental methodologist with deep expertise in: (1) local LLM inference (Ollama, llama.cpp, vLLM, SGLang), (2) model quantization and efficiency, (3) prompt engineering and automatic prompt optimization (DSPy, OPRO, APE), (4) experimental design for LLM system comparison, and (5) cost-quality tradeoff analysis for LLM-based pipelines. You have been given context describing:

- **Our research fork's experiment framework** (forked from the published Harmonia/BDI-Kit system, Lopez et al., 2026): YAML-configured experiments with automated execution via ExperimentRunner, SLURM job generation, per-experiment run IDs, Phoenix/OTel tracing with token/cost tracking, and a Plotly Dash dashboard for comparison. The published BDI-Kit/Harmonia system does not include this experiment infrastructure — it was built as part of the research fork.
- **Current local model support**: Ollama with per-job isolation (unique port, PID file), VRAM estimation, dynamic context length configuration. Models tested include Qwen 3.5 (4B, 9B, 27B), Mistral Nemo, Devstral, Nemotron Nano, Gemma 3 27B.
- **Provider support**: 100+ models via litellm. Provider prefix mapping for Ollama, OpenAI, OpenRouter, Anthropic. OpenRouter hardening for resilience.
- **The ConstruM paper**: Investigating optimal context selection for LLM-based schema matching — directly relevant to prompt optimization.
- **The recursive language models paper**: Master LLM + sub-LLM decomposition for scaling to longer contexts.

**Your task is to produce an exhaustive research report** that addresses:

> ***How should we select, configure, and optimize local and frontier LLMs for omics metadata harmonization — including quantization, inference frameworks, prompt optimization, and rigorous experimental methodology for comparing configurations — to produce publishable scientific results?***

---

## PART 1: LOCAL LLM INFERENCE INFRASTRUCTURE

### 1.1 Inference Framework Comparison

Compare the following frameworks for running local models on the HPC cluster (SLURM, NVIDIA GPUs — likely A100/A40/RTX6000):

1. **Ollama** (current setup): Easy model management, REST API, automatic quantization selection. Limitations: Limited batching, no speculative decoding, context length defaults to 4096 (must override), single-request inference, no tensor parallelism.

2. **llama.cpp / llama-server**: Direct GGUF model loading, speculative decoding support, grammar-based constrained generation, better quantization control (GGUF Q4_K_M, Q5_K_M, Q6_K, Q8_0, F16). **Search for**: llama.cpp server mode for agent use. Grammar-constrained generation for structured output.

3. **vLLM**: PagedAttention for efficient KV cache, continuous batching, tensor parallelism for multi-GPU. Better throughput for batch experiments. **Search for**: vLLM vs Ollama performance comparison 2025 2026. Can vLLM serve as a drop-in for Ollama?

4. **SGLang**: RadixAttention for efficient prefix caching, structured generation, multi-turn optimization. **Search for**: SGLang for agent workloads 2025 2026.

5. **TGI (Text Generation Inference)**: HuggingFace's inference server. Flash Attention, continuous batching. **Search for**: TGI vs vLLM comparison 2025.

For each: describe installation on HPC (Apptainer/Singularity compatibility), GPU memory requirements, throughput for typical agent workloads (multi-turn conversations with tool calls), and compatibility with litellm.

### 1.2 Model Selection for Metadata Harmonization

Which models should be tested? Organize by capability tier.

**Critical insight from Matchmaker (Seedat & van der Schaar, 2024)**: A compositional multi-stage pipeline with GPT-3.5 achieves comparable performance to a single-stage pipeline with GPT-4 on schema matching (Table 6 in their paper: Matchmaker GPT-3.5 acc@1 48.30% on MIMIC vs. ReMatch GPT-4 acc@1 42.50%). This means **pipeline architecture and model choice interact strongly** — we cannot test models independently of architecture. A weaker model with a better pipeline may outperform a stronger model with a simpler pipeline. Our experimental design must account for this interaction by testing at least the top model from each tier with at least two architectures.

**Tier 1: Frontier models (cloud API)**
- Claude Sonnet 4.6, Claude Opus 4.6 (Anthropic)
- GPT-5-mini, GPT-5-nano (OpenAI)
- Gemini 2.5 Flash, Gemini 3 Flash Preview (Google)
- **Search for**: Latest frontier model capabilities for structured data tasks as of early 2026

**Tier 2: Mid-range models (cloud or local with ~40GB VRAM)**
- Qwen 3.5 27B — **Search for**: Qwen 3.5 performance on data tasks, tool calling capability
- Gemma 3 27B — How does it compare to Qwen 3.5 27B?
- Devstral (Mistral) — Coding-focused. How good at structured data tasks?
- DeepSeek V3.2 — **Search for**: DeepSeek V3.2 availability and performance for agent tasks
- Kimi K2.5 — **Search for**: Kimi K2.5 capabilities for data processing

**Tier 3: Small models (<16GB VRAM, can run on consumer GPUs)**
- Qwen 3.5 4B, 9B — Can small Qwen models handle metadata harmonization?
- Mistral Nemo (12B) — The smallest model currently tested
- Nemotron Nano — NVIDIA's small model. **Search for**: Nemotron Nano tool calling performance
- Phi-4 / Phi-4-mini — **Search for**: Microsoft Phi-4 for structured data tasks
- Llama 3.3 / Llama 4 Scout — **Search for**: Latest Llama models for agent tasks

**For each model**: report parameter count, context window, tool calling support (native JSON vs. requires prompting), recommended quantization for target GPU, approximate tokens/second at that quantization, and whether it has been tested for data integration tasks.

### 1.3 Quantization Impact on Harmonization Quality

**This is a key variable to test.** Different quantization levels trade off quality for speed/VRAM:

1. **GGUF quantization levels**: Q4_K_M (4-bit), Q5_K_M (5-bit), Q6_K (6-bit), Q8_0 (8-bit), F16 (full). How much quality degradation occurs at each level for a structured task like metadata harmonization?

2. **GPTQ / AWQ**: Alternative quantization approaches available through vLLM. **Search for**: GPTQ vs GGUF quality comparison for structured tasks.

3. **The quality-cost curve**: For a given budget (GPU-hours), is it better to run a larger model at lower quantization or a smaller model at higher quantization?

4. **How to measure quantization impact**: Run the same benchmark tasks with the same model at different quantization levels. Report the accuracy degradation curve.

**Search for**: "quantization impact LLM structured tasks 2025 2026" and "GGUF Q4 Q8 quality comparison agent"

---

## PART 2: PROMPT OPTIMIZATION

### 2.1 The ConstruM Insight: Context Selection Matters

The ConstruM paper investigates which context elements most affect LLM schema matching performance. Detail:

1. **What context elements were tested?** Column names, data types, sample values, foreign key relationships, table descriptions, example mappings.
2. **Which elements had the highest impact?** Rank them by importance.
3. **What is the optimal context composition for schema matching?** How does this translate to the GEO metadata harmonization task?
4. **Does the optimal context differ by model?** Do frontier models need less context than local models?

### 2.2 Prompt Optimization Approaches

1. **Manual prompt engineering**: The current approach in our research fork. System prompts are Jinja2 templates in `prompts/`. Versioned prompt variants in `experiments/.../configs/prompts/`.

2. **DSPy** (Stanford NLP): Automatic prompt optimization through compilation. **Search for**: 
   - "DSPy prompt optimization 2025 2026 latest" — what has changed since the original paper?
   - "DSPy structured data task" — has it been applied to schema matching or data integration?
   - **Critical methodological concern**: DSPy optimizes prompts on a training set. For our benchmark, we must use a separate test set that the prompts were not optimized on. How to properly split the benchmark for this? What is the minimum training set size for DSPy to converge?
   - **Matchmaker validation of this approach**: Matchmaker (Seedat & van der Schaar, 2024) directly validates DSPy bootstrapping for schema matching. Their key findings: (a) Optimized in-context examples yield +5% acc@1 over vanilla on MIMIC-OMOP (Table 2); (b) Systematic selection of in-context examples outperforms random selection, confirming the optimization matters; (c) The optimization uses an LLM Evaluator to score traces on an unlabeled evaluation set — no gold-standard labels needed for the optimization itself (though labels ARE needed for the final test evaluation). (d) They use at most 4 synthetic in-context examples. For our project: we should replicate this approach for each stage of our pipeline (schema matching prompts, value mapping prompts, etc.) and compare optimized vs. vanilla vs. random. The critical addition is that we have labeled gold standards, so we can measure the actual improvement rather than relying solely on an LLM evaluator.

3. **OPRO** (Yang et al., 2023): LLM-based prompt optimization. **Search for**: OPRO for structured tasks. How does it compare to DSPy?

4. **APE (Automatic Prompt Engineer)**: **Search for**: Latest APE approaches 2025 2026.

5. **Meta-prompting**: Using an LLM to generate and evaluate prompts. **Search for**: Meta-prompting for domain-specific tasks.

6. **Few-shot example selection**: Which few-shot examples to include in the prompt? Random vs. similarity-based selection vs. diverse selection. Matchmaker constructs its evaluation set by stratifying into "easy queries" (high semantic similarity) and "challenging queries" (low semantic similarity) — this stratification strategy should be adopted for our benchmark. **Search for**: Few-shot example selection strategies for LLM data tasks.

### 2.3 What to Optimize

The harmonization pipeline has multiple prompts that could be independently optimized:

1. **System prompt**: The overall instructions for the agent
2. **Tool descriptions**: How each tool is described to the LLM
3. **Schema representation**: How the GDC schema is presented (full JSON, summarized, example-based)
4. **Example mappings**: Few-shot examples of correct column mappings
5. **Value mapping instructions**: How to instruct the LLM to transform values
6. **Error recovery prompts**: What to say when the LLM makes a mistake

For each: what is the search space? How many tokens does each variant add? What is the expected impact on performance?

---

## PART 3: EXPERIMENTAL METHODOLOGY FOR PUBLISHABLE RESULTS

### 3.1 Experimental Design

Design a rigorous experimental framework:

1. **Independent variables**: LLM model, agent architecture (ReAct/CodeAct/multi-agent/frontier), quantization level, prompt variant, context content, temperature, number of example values per column, ontology access method
2. **Dependent variables**: Schema mapping F1, value mapping accuracy, token usage, wall-clock time, cost (USD), success rate (fraction of runs that produce valid output), failure mode distribution
3. **Control variables**: Same benchmark dataset, same gold standard, same evaluation code, same hardware (or controlled hardware allocation)

**How many runs per configuration?** LLM outputs are stochastic. At temperature 0.0, variance is minimal but not zero (due to batching effects). At temperature > 0, significant variance. **Search for**: "LLM experiment variance replication" — how many runs are standard in LLM evaluation papers? Recommendation: ≥3 runs per configuration at temperature 0.0, ≥5 at temperature > 0.

**How to handle the combinatorial explosion?** With ~10 models × 3 architectures × 3 prompt variants × 3 quantization levels = 270 configurations × 3 runs = 810 experiments on the simplest benchmark task alone. This is infeasible.

Propose a **sequential experimentation strategy**:
- Phase 1: Screen models (fix architecture, fix prompt). Identify top-3 models per tier.
- Phase 2: Screen architectures (fix model to tier-1 best, fix prompt). Identify best architecture.
- Phase 3: Screen prompts (fix model, fix architecture). Identify best prompt.
- Phase 4: Full factorial on the top configurations only.
- Phase 5: Ablation studies on individual components.

**Search for**: "sequential experimental design LLM evaluation" and "efficient hyperparameter search LLM" — what design-of-experiments approaches are used in the LLM evaluation literature?

### 3.2 Statistical Analysis

1. **Paired comparisons**: McNemar's test for column mapping (binary per-column outcomes). Wilcoxon signed-rank for continuous metrics (F1, accuracy).
2. **Multiple testing correction**: Bonferroni or Holm-Bonferroni for multiple model comparisons.
3. **Effect size reporting**: Cohen's d or Cliff's delta.
4. **Confidence intervals**: Bootstrap 95% CIs for all reported metrics.
5. **Ablation analysis**: When removing a component (e.g., ontology access), what is the marginal effect?

**Search for**: "statistical methodology LLM benchmark paper 2025" — what statistical practices are expected in top-tier AI venues?

### 3.3 Cost-Quality Analysis

A key practical contribution: what is the cost to achieve a given quality level?

1. **Cost model**: Input tokens × input price + output tokens × output price. Include Ollama electricity cost for local models.
2. **Quality-cost Pareto frontier**: Plot quality (F1) vs. cost per table for all configurations. Identify the Pareto-optimal set.
3. **Time-quality tradeoff**: Similar analysis for wall-clock time.
4. **Practical recommendations**: "For budget X, use model Y with architecture Z to achieve quality W."

### 3.4 Reporting Standards

What should a benchmark paper in this domain report?

1. **Per-model, per-task result tables** with confidence intervals
2. **Failure mode distribution** per model/architecture
3. **Example qualitative outputs**: Show specific correct and incorrect mappings to illustrate model behavior
4. **Reproducibility package**: All code, configs, prompts, and evaluation scripts. Docker/Apptainer image specification.
5. **Leaderboard**: A publicly available leaderboard (GitHub + HuggingFace) for the omics metadata harmonization benchmark

**Search for**: "benchmark paper reporting best practices NeurIPS 2025" and "LLM evaluation reproducibility checklist"

---

## PART 4: HANDLING THE TIMELINE AND PRIORITIZATION

### 4.1 What Can Be Done in 6 Months

Given one researcher (PhD student) working full-time with GPU access and the existing research fork codebase:

**Month 1**: Infrastructure + benchmark construction
**Month 2**: Model screening experiments
**Month 3**: Architecture comparison experiments
**Month 4**: Prompt optimization + ablation studies
**Month 5**: End-to-end pipeline + analysis
**Month 6**: Paper writing + reproducibility package

Is this realistic? What are the bottlenecks? What can be parallelized?

### 4.2 First Publication vs. Future Work

**P1 — For the first publication**: What is the core benchmark + core experiment set that produces a novel, publishable contribution?

Proposal: 
- Benchmark: Task Level 1 (single table to GDC) + Task Level 2 (schema + value mapping) on 5–10 GEO tables with gold standards
- Experiments: 5–8 LLMs × 3 architectures × best prompt = ~15–24 configurations × 3 runs
- Analysis: Per-model comparison, architecture comparison, failure taxonomy, cost-quality analysis
- Novelty: First domain-specific benchmark for omics metadata harmonization + first systematic comparison of LLM models/architectures on this task

**P2 — Strengthens the first publication if time allows**: Ablation studies (context content, candidate generation strategy per Matchmaker), additional local model sweep, quantization impact curves, prompt optimization comparison (manual vs. DSPy-bootstrapped)

**P3 — Stretch / second publication**: N-table harmonization, search pipeline evaluation, multi-agent architectures, end-to-end pipeline, cross-schema generalization (GDC vs. other target schemas)

**P-Extra — Future research directions**: DSPy optimization at scale with large benchmark, paper full-text integration for search, production deployment with human-in-the-loop UI, ontology-augmented harmonization, fine-tuning local models on the benchmark data

---

## SEARCH QUERIES TO EXECUTE

1. "Ollama vs vLLM vs llama.cpp performance comparison 2025 2026"
2. "SGLang agent workload structured generation"
3. "Qwen 3.5 tool calling performance benchmark"
4. "GGUF quantization quality impact structured tasks"
5. "DSPy prompt optimization structured data 2025 2026"
6. "OPRO automatic prompt engineer comparison"
7. "LLM experiment variance replication methodology"
8. "sequential experimental design LLM evaluation"
9. "statistical methodology LLM benchmark paper"
10. "cost-quality tradeoff LLM inference 2025"
11. "LLM evaluation reproducibility checklist"
12. "Phi-4 structured data task performance"
13. "Llama 4 Scout tool calling agent"
14. "local LLM grammar constrained generation JSON"
15. "benchmark paper reporting NeurIPS best practices"

---

## CRITICAL REMINDERS

- **The HPC environment constrains choices.** Solutions must work with SLURM + Apptainer + NVIDIA GPUs. Cloud-only approaches are secondary.
- **Local models are a core variable.** The paper should demonstrate whether local models can approach frontier model performance for this specific task.
- **Statistical rigor is non-negotiable.** Every comparison must have proper statistical tests, multiple runs, and confidence intervals.
- **Cost analysis is a practical contribution.** Academic labs need to know what they can achieve with limited budgets.
- **DSPy and prompt optimization require proper train/test splits.** The benchmark must be large enough to support this.
- **The first publication's P1 experiments should be achievable in 6 months.** But do not omit P2/P3/P-Extra experiments from the analysis — classify them with estimated time and effort so the full research line is visible. A synthesis document that only covers what fits in 6 months is incomplete as a research planning tool.
