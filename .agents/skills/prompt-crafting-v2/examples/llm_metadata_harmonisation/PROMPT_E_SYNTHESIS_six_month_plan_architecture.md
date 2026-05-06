# Deep Research Prompt E (SYNTHESIS): Six-Month Research Plan and Codebase Architecture for LLM-Based Omics Metadata Harmonization

---

## PREAMBLE AND INSTRUCTIONS TO THE RESEARCH AGENT

You are a principal investigator and systems architect with deep expertise in: (1) computational biology research planning, (2) LLM-based data integration system design, (3) scientific benchmarking methodology, and (4) software architecture for research pipelines. You have been given **four detailed research reports** from prior deep research rounds, covering:

- **Report A** (Schema Matching & Harmonization Landscape): Comprehensive review of classical, embedding-based, and LLM-based schema matching approaches; benchmark design for omics metadata harmonization; failure mode taxonomy; comparison methodology for Valentine, LLMatch, Magneto, BDI-Kit, and frontier coding agents.
- **Report B** (RAG & GEO Search Discovery): RAG architecture design for GEO dataset discovery; retrieval strategy comparison (BM25, dense, hybrid, ColBERT, agentic); evaluation framework with semi-gold-standard GEO ID sets; paper full-text integration cost-benefit; search-to-harmonization handoff.
- **Report C** (Agent Architectures): Single-agent (ReAct, CodeAct, frontier coding agent) vs. multi-agent (hierarchical, fan-out, recursive, critic) comparison; observability and tracing; sandboxed execution; the simplicity vs. capability tradeoff; human-in-the-loop interface patterns.
- **Report D** (Local LLMs, Optimization, Methodology): Local inference frameworks (Ollama, vLLM, llama.cpp, SGLang); model selection across tiers; quantization impact; prompt optimization (DSPy, manual, ConstruM-informed); experimental design with sequential screening; statistical analysis; cost-quality analysis; timeline feasibility.

You also have context from:

- **Our research codebase** (a heavily extended fork of the published Harmonia/BDI-Kit system, as described in `how_this_codebase_works_02_04_2026.md`): A working metadata harmonization agent with two primary agent paradigms (ReAct + BDI-Kit domain tools, and true CodeAct), Apptainer sandboxing, Phoenix/OTel tracing, Plotly Dash dashboard, YAML-configured experiments, 20-class failure taxonomy, evaluation pipeline with `calculate_all_metrics()`. The published BDI-Kit/Harmonia (Lopez et al., Patterns 2026) is a separate citable artifact that provides the base tools but not the experiment infrastructure.
- **Matchmaker** (Seedat & van der Schaar, NeurIPS GenAI for Health 2024): A compositional LM program for schema matching using ColBERTv2 multi-vector retrieval + LLM reasoning candidates → refinement → MCQ confidence scoring. Key findings directly relevant to our experimental design: (a) compositional pipeline with GPT-3.5 ≈ simple pipeline with GPT-4; (b) DSPy bootstrapping for zero-shot self-improvement works (+5% acc@1); (c) reasoning-based candidates > semantic-only; (d) entropy-based human deferral outperforms random. No code published; tested on MIMIC-OMOP and Synthea-OMOP (clinical, not omics). This is the current SOTA for zero-shot LLM-based schema matching on medical benchmarks and should be reimplemented as a key comparison system.
- **The GEO metadata database plan** (`final_implementation_plan_GEO_db.md`): SQLite-based database with multi-stage extraction, FTS5 search, incremental sync.
- **SRAgent reusable patterns**: Agent-as-tool factory, centralized model factory, structured output with retry, fan-out/fan-in, per-agent configuration, step detection.
- **The draft introduction** listing 7 claimed contributions: Gene Expression Omnibench benchmark suite, frontier+local LLM comparison, GEO-specific RAG performance, paper embedding improvements, end-to-end pipeline evaluation, failure mode taxonomy, default schema options.

**Your task is to synthesize all four reports into three concrete deliverables:**

> **Deliverable 1**: A prioritized, time-bound **six-month research plan** with specific experiments, dependencies, go/no-go decisions, risk × yield scoring, and month-by-month milestones. Experiments are classified as P1 (essential), P2 (important, aim to complete), P3 (stretch, may spill past 6 months), and P-Extra (aspirational, future work). The 6-month timeline covers P1 and P2; P3 experiments appear as stretch goals with estimated additional time; P-Extra experiments are fully specified in the roadmap.
>
> **Deliverable 2**: A **proposed codebase architecture** for the full envisioned system (not just the P1 subset), with specific components, interfaces, and a diff from the current research fork. Clearly mark which components are P1 (build now), P2 (build if time allows), P3 (design interface now, implement later), and P-Extra (future). The architecture should be designed so that P1 work creates foundations that P2/P3 naturally extends.
>
> **Deliverable 3**: A **research roadmap beyond 6 months** — a 1–2 page outline of how the P3 and P-Extra experiments, additional benchmarks, multi-agent architectures, and end-to-end pipeline work could unfold over a 12–18 month horizon, including potential second and third publications. This is not a wish list — each item should have a concrete description, estimated effort, and connection to the overall research narrative.

---

## DELIVERABLE 1: SIX-MONTH RESEARCH PLAN

### Prioritization Framework

Use the following scoring criteria for each experiment/task:

| Criterion | Score range | Description |
|-----------|------------|-------------|
| **Simplicity** | 1–5 | How easy to implement given current infrastructure (5 = trivial) |
| **Yield** | 1–5 | How much scientific insight or paper content this produces (5 = a paper section on its own) |
| **Risk** | 1–5 | Probability of useful result (5 = near certain) |
| **Novelty** | 1–5 | How novel is this contribution (5 = unprecedented in the field) |
| **Dependencies** | List | What must be completed first |

**Priority Score = (Yield × Risk × Novelty) / (6 − Simplicity)**

**Priority classification** — after scoring, assign each experiment a priority level:
- **P1 (Essential)**: Experiments without which the first publication cannot stand. These form the irreducible core: benchmark construction, key baselines, the central model/architecture comparison, and statistical analysis. If nothing else gets done, P1 produces a publishable paper.
- **P2 (Important)**: Experiments that substantially strengthen the first publication and are feasible within the 6-month window. These differentiate a good paper from a great one: ablation studies, additional model comparisons, prompt optimization, value mapping analysis. Aim to complete all P2, but they can be deprioritized if P1 takes longer than expected.
- **P3 (Stretch)**: Experiments that push the boundaries of what one researcher can achieve in 6 months. These are fully specified and ready to execute, but may spill into month 7–8 or become the core of a second publication: N-table harmonization, multi-agent architectures, end-to-end pipeline, search pipeline evaluation.
- **P-Extra (Aspirational / Future Work)**: High-value ideas that require substantial additional infrastructure, collaborations, or data beyond what is immediately available. These should be articulated with the same specificity as P1–P3 (protocols, expected outcomes, estimated effort) so they can be picked up immediately when capacity allows. They form the basis for Deliverable 3 (the research roadmap): DSPy optimization at scale, paper full-text integration, cross-schema generalization, production deployment, etc.

### Experiment Inventory

Before creating the timeline, score and rank ALL of the following experiments. Assign each a Priority level (P1/P2/P3/P-Extra). **Do not remove experiments from the inventory based on feasibility — instead, classify them.** Add any experiments identified in Reports A–D that are missing from this list. The inventory should be comprehensive: it represents the full research vision, not just what fits in 6 months.

| ID | Experiment | Simplicity | Yield | Risk | Novelty | Dependencies | Priority |
|----|-----------|------------|-------|------|---------|-------------|
| **Benchmark Construction** |
| B1 | Construct single-table-to-GDC gold standards (5–10 GEO tables + expert-annotated mappings) | 3 | 5 | 5 | 4 | None |
| B2 | Construct two-table harmonization gold standards (3–5 pairs) | 2 | 4 | 4 | 4 | B1 |
| B3 | Construct N-table harmonization gold standard (CPTAC 10-table set with Li 2023 ground truth) | 3 | 4 | 4 | 3 | B1 |
| B4 | Construct GEO search query + gold-standard ID sets (10–30 queries) | 3 | 4 | 3 | 4 | None |
| B5 | Implement automated evaluation pipeline (extending current calculate_all_metrics()) | 4 | 3 | 5 | 1 | B1 |
| **Schema Matching Experiments** |
| S1 | Valentine baselines on omics benchmark (COMA, Cupid, Similarity Flooding, Jaccard-Levenshtein) | 4 | 3 | 5 | 2 | B1 |
| S2 | Embedding model comparison (5–8 models) on omics benchmark | 3 | 3 | 4 | 3 | B1 |
| S3 | Frontier LLM screening: Claude Sonnet 4.6, GPT-5-mini, Gemini Flash on single-table task (3 architectures: ReAct+tools, CodeAct, frontier coding agent) | 3 | 5 | 4 | 3 | B1, B5 |
| S4 | Local LLM screening: Qwen 3.5 27B, Mistral Nemo, Devstral, Gemma 3 27B (3 architectures: ReAct+tools, CodeAct, frontier coding agent) | 3 | 5 | 3 | 4 | B1, B5 |
| S5 | Small local LLM screening: Qwen 3.5 4B/9B, Phi-4, Nemotron Nano | 3 | 4 | 3 | 4 | B1, B5 |
| S6 | Frontier coding agent baseline: Claude Code + Codex in full-auto mode on same tasks | 3 | 5 | 3 | 5 | B1 |
| S7 | Reimplement Matchmaker compositional LM program (candidate gen → refinement → MCQ scoring) on omics benchmark; no code published but Algorithm 2 + Appendix C prompts in paper provide sufficient detail | 2 | 5 | 4 | 5 | B1 |
| S7b | Run LLMatch / Magneto comparison on omics benchmark (if code available) | 2 | 4 | 3 | 4 | B1 |
| S8 | Context content ablation (per ConstruM): vary sample values, schema representation, ontology access. Also test Matchmaker's dual candidate generation insight: semantic-only vs. reasoning-only vs. combined | 3 | 4 | 4 | 3 | S3 |
| S9 | Temperature and reasoning settings ablation | 4 | 2 | 4 | 2 | S3 |
| **Value Mapping Experiments** |
| V1 | Value mapping comparison: LLM-based vs. dictionary lookup vs. ontology matching | 3 | 4 | 4 | 3 | B1 |
| V2 | Constrained generation for value mapping (grammar-based with llama.cpp, or function calling) | 2 | 3 | 3 | 4 | V1 |
| **Multi-table Experiments** |
| M1 | Two-table harmonization with best single-table config | 3 | 4 | 3 | 3 | S3, B2 |
| M2 | N-table harmonization (10 CPTAC tables) | 2 | 5 | 2 | 4 | M1, B3 |
| M3 | Multi-agent vs. single-agent for N-table harmonization | 2 | 5 | 2 | 5 | M2 |
| **Prompt Optimization** |
| P1 | Manual prompt optimization based on error analysis from S3/S4 | 4 | 3 | 4 | 2 | S3 |
| P2 | DSPy prompt optimization (requires train/test split of benchmark) | 2 | 4 | 3 | 4 | B1 (with ≥20 tables) |
| **Search Pipeline Experiments** |
| R1 | Implement basic GEO search: BM25 over SQLite FTS5 | 4 | 3 | 5 | 2 | GEO database built |
| R2 | Dense embedding retrieval: embed all GEO Series, test with gold-standard query sets | 3 | 4 | 4 | 3 | R1, B4 |
| R3 | Hybrid retrieval (BM25 + dense) with RRF | 3 | 3 | 4 | 2 | R1, R2 |
| R4 | LLM reranking of search results | 3 | 3 | 3 | 3 | R2 |
| R5 | Paper full-text embedding + retrieval | 2 | 3 | 3 | 3 | R2, papers downloaded |
| R6 | Agentic multi-step search with query refinement | 2 | 4 | 2 | 4 | R3 |
| **End-to-End** |
| E1 | End-to-end pipeline: search → harmonize on gold-standard queries | 2 | 5 | 2 | 5 | R3, M1 |
| E2 | Failure mode taxonomy documentation (from all experiments) | 4 | 4 | 5 | 3 | S3, S4 |
| **Architecture** |
| A1 | Implement per-agent model configuration (SRAgent Pattern 2) | 3 | 2 | 4 | 2 | None |
| A2 | Implement structured output validation (SRAgent Pattern 3) | 3 | 3 | 4 | 2 | None |
| A3 | Implement streaming progress display (SRAgent Pattern 7) | 4 | 1 | 5 | 1 | None |
| A4 | Add quantization-level sweep support to experiment configs | 4 | 2 | 5 | 2 | None |

**Calculate Priority Scores and rank all experiments.** Assign priority levels. Then map P1 and P2 experiments onto the 6-month timeline below. P3 experiments should appear at the end of the timeline with a "stretch goal" marker. P-Extra experiments should be fully described in the research roadmap (Deliverable 3).

### Month-by-Month Timeline (P1 + P2 experiments)

#### Month 1: Foundation, Benchmark Construction, and Quick Wins

**Week 1–2: Benchmark gold standard construction**
- [ ] B1: Construct 5–10 single-table GEO benchmarks with gold-standard column mappings to GDC. Source tables from: Dou 2020 (existing), CPTAC studies (existing Li 2023 ground truth), 3–5 new GEO studies representing different cancer types and metadata complexity levels.
- [ ] B4: Define 10–15 search queries with semi-gold-standard GEO ID sets (leverage existing ALL methylation IDs + construct 5–10 additional query sets).
- [ ] B5: Extend `calculate_all_metrics()` to support the new benchmark format.
- **Deliverables**: Benchmark dataset v1.0, evaluation pipeline v2.0
- **Go/no-go**: If gold standards cannot be constructed for ≥5 tables by end of week 2, narrow to 3 tables and proceed.

**Week 2–4: Valentine baselines + frontier model screening**
- [ ] S1: Run Valentine baselines (install `valentine`, run all matchers on benchmark tables)
- [ ] S3: Run top-3 frontier models × 3 architectures (ReAct+tools, CodeAct, frontier coding agent) = 9 configurations × 3 runs = 27 experiments
- [ ] S6: Run Claude Code and Codex in full-auto mode on same benchmark (critical baseline)
- [ ] E2 (start): Begin documenting failure modes from each run
- **Deliverables**: Valentine baseline results, frontier model results, first failure mode observations
- **Person-hours**: ~80–100
- **Compute**: ~50 frontier model API calls (modest cost at ~$0.50–2.00 each)

**Go/no-go decision (end of Month 1)**: Do LLM-based approaches outperform Valentine baselines? If not, investigate why before proceeding. Does the bespoke pipeline outperform frontier coding agents? This determines the narrative of the paper.

---

#### Month 2: Local Model Screening and Architecture Comparison

**Week 5–6: Local model experiments**
- [ ] S4: Run top-4 mid-range local models × best architecture from Month 1 (4 × 3 runs = 12 experiments)
- [ ] S5: Run top-3 small local models (3 × 3 runs = 9 experiments)
- [ ] A4: Implement quantization sweep support and run Q4/Q6/Q8/F16 comparison for best local model
- **Deliverables**: Local vs. frontier comparison table, quantization impact curves

**Week 7–8: Architecture deep-dive + embedding baselines**
- [ ] S2: Run embedding model comparison (5 models on benchmark)
- [ ] S8: Context content ablation with best frontier model (vary sample values 0/5/10/20, schema representation, ontology access)
- [ ] S7: Run LLMatch/Magneto/MatchMaker if code available (may require significant setup time — allocate 2 weeks, with fallback to reporting "could not reproduce")
- **Deliverables**: Architecture comparison results, context ablation results, embedding baselines

**Go/no-go decision (end of Month 2)**: Which architecture wins? ReAct + tools, CodeAct, or frontier coding agent? This determines the focus for the remaining months.

---

#### Month 3: Value Mapping, Multi-Table, and Search Pipeline

**Week 9–10: Value mapping and two-table harmonization**
- [ ] V1: Value mapping comparison using best configuration from Month 2
- [ ] B2: Construct two-table gold standards
- [ ] M1: Two-table harmonization experiments
- **Deliverables**: Value mapping results, two-table results

**Week 11–12: Search pipeline v1**
- [ ] R1: Implement BM25 search over GEO database (requires GEO database to be built — this may need to start in Month 1 as background task)
- [ ] R2: Embed GEO Series descriptions with best embedding model from S2
- [ ] R3: Hybrid retrieval with RRF
- [ ] Test search on gold-standard query sets from B4
- **Deliverables**: Search pipeline v1, retrieval evaluation results

---

#### Month 4: Prompt Optimization, N-Table, and Ablations

**Week 13–14: Prompt optimization**
- [ ] P1: Manual prompt optimization based on Month 1–3 error analysis
- [ ] P2 (if benchmark ≥20 tables): DSPy prompt optimization with proper train/test split
- **Deliverables**: Optimized prompts, before/after comparison

**Week 15–16: N-table and search refinement**
- [ ] M2: N-table harmonization (10 CPTAC tables) with best configuration
- [ ] R4: LLM reranking for search
- [ ] R5 (optional): Paper full-text integration if time permits
- **Deliverables**: N-table results, improved search results

---

#### Month 5: End-to-End Pipeline and Analysis

**Week 17–18: End-to-end experiments**
- [ ] E1: Run full pipeline (search → harmonize) on gold-standard queries
- [ ] E2 (complete): Finalize failure mode taxonomy with examples from all experiments

**Week 19–20: Comprehensive analysis**
- [ ] Statistical analysis of all results (paired tests, confidence intervals, effect sizes)
- [ ] Cost-quality Pareto frontier plots
- [ ] Qualitative analysis of failure modes
- [ ] Generate all figures and tables for the paper
- **Deliverables**: Complete analysis, all figures/tables

---

#### Month 6: Paper Writing and Reproducibility

**Week 21–22: Paper draft**
- [ ] Introduction (revise draft introduction with concrete results)
- [ ] Methods (benchmark construction, experimental setup, evaluation metrics)
- [ ] Results (schema matching comparison, architecture comparison, local vs. frontier, search pipeline, end-to-end)
- [ ] Discussion (failure modes, practical recommendations, limitations)

**Week 23–24: Reproducibility and submission**
- [ ] Reproducibility package: code, configs, docker/apptainer images, benchmark data
- [ ] Publicly release Gene Expression Omnibench on GitHub + HuggingFace
- [ ] Internal review and revision
- **Deliverables**: Complete paper draft, reproducibility package, public benchmark

---

### Contingency Plans

**If benchmark gold standard construction takes longer than 2 weeks**: Use only Dou 2020 + CPTAC tables with Li 2023 ground truth (already available). This gives ≥4 tables — sufficient for initial experiments.

**If frontier coding agents outperform the bespoke pipeline**: This is itself a major finding. The paper becomes: "Off-the-shelf coding agents match or exceed specialized tools for omics metadata harmonization — implications for the field." This is arguably more impactful than showing a specialized tool wins.

**If local models perform poorly**: Focus the paper on frontier model comparison + failure taxonomy + practical guidelines. The local model results become a section showing the quality gap and its implications for budget-constrained labs.

**If GEO database construction is not complete by Month 3**: Use a subset of GEO (e.g., all human cancer studies, ~50K series) and report the search results as preliminary. The full database can be completed post-publication.

**If LLMatch/Magneto code is not available**: Report this as a limitation. Run the Valentine baselines + embedding baselines as comparison points. Cite their published results on other domains.

---

### Resource Requirements

| Resource | Quantity | Estimated Cost |
|----------|----------|---------------|
| GPU compute (A100/A40) | ~200 GPU-hours total | Free (institutional HPC) |
| Frontier model API costs | ~500–1000 API calls | ~$200–500 |
| Storage for GEO database + embeddings | ~200 GB | Free (HPC storage) |
| Expert annotation time for gold standards | ~40–60 person-hours | In-kind (lab members) |
| Paper full-text downloads | ~150K papers (optional) | ~100 GB storage + download time |

---

## DELIVERABLE 2: PROPOSED CODEBASE ARCHITECTURE

### Current vs. Proposed Architecture

**What exists (current research fork, based on published Harmonia/BDI-Kit)**:
```
harmonia/
├── src/automation/          # Experiment runner + tracing
├── src/bdikit_context/      # ReAct + domain tools agent
├── src/codeact_context/     # CodeAct agent
├── src/evaluation/          # Metrics + visualization
├── src/dashboard/           # Plotly Dash UI
├── src/context_management/  # Kernel state budget
├── experiments/             # YAML configs + prompts
└── scripts/                 # Dashboard, Phoenix, utils
```

**What is proposed (v2 — "GEO-Harmonizer")**:
```
geo-harmonizer/
├── src/
│   ├── core/                    # Shared infrastructure
│   │   ├── model_factory.py     # NEW: Multi-model support (SRAgent Pattern 2)
│   │   ├── structured_output.py # NEW: Pydantic validation + retry (SRAgent Pattern 3)
│   │   ├── tracing.py           # EVOLVED: Extended for multi-agent traces
│   │   └── config.py            # EVOLVED: Phase-specific model/temperature overrides
│   │
│   ├── search/                  # NEW: GEO search pipeline
│   │   ├── geo_database/        # From geo_metadata_db plan (SQLite + FTS5)
│   │   ├── embeddings/          # Vector store for GEO descriptions
│   │   ├── retrieval.py         # Hybrid retrieval (BM25 + dense + reranking)
│   │   ├── query_expansion.py   # LLM-based query expansion
│   │   └── evaluation.py        # Search-specific evaluation metrics
│   │
│   ├── harmonization/           # EVOLVED from current src/
│   │   ├── agents/              # Agent implementations
│   │   │   ├── bdikit_agent.py  # EVOLVED: ReAct + domain tools
│   │   │   ├── codeact_agent.py # EVOLVED: CodeAct
│   │   │   ├── coding_agent.py  # NEW: Minimal coding agent (bash + read + write)
│   │   │   ├── compositional.py # NEW: Matchmaker-style fixed pipeline (candidate gen → refine → score)
│   │   │   └── multi_agent.py   # NEW: Hierarchical multi-agent (optional)
│   │   ├── prompts/             # EVOLVED: Versioned Jinja2 templates
│   │   ├── tools/               # EVOLVED: BDI-Kit tools + new tools
│   │   └── materialize.py       # Deterministic mapping code generator
│   │
│   ├── evaluation/              # EVOLVED from current src/evaluation/
│   │   ├── metrics.py           # Core metrics (schema matching + value mapping)
│   │   ├── benchmark.py         # NEW: Benchmark task runner
│   │   ├── comparison.py        # NEW: Multi-config statistical comparison
│   │   └── visualization.py     # EVOLVED: Publication-quality plots
│   │
│   ├── dashboard/               # EVOLVED from current src/dashboard/
│   │   └── ...                  # Add search pipeline tabs, multi-agent trace views
│   │
│   └── experiment/              # EVOLVED from src/automation/
│       ├── runner.py            # EVOLVED: Supports multi-agent configs
│       ├── sweep.py             # NEW: Automated parameter sweeps
│       └── analysis.py          # NEW: Post-experiment statistical analysis
│
├── benchmark/                   # NEW: Gene Expression Omnibench
│   ├── tasks/
│   │   ├── single_table_gdc/    # Task Level 1–2 gold standards
│   │   ├── two_table/           # Task Level 3 gold standards
│   │   ├── n_table/             # Task Level 4 gold standards
│   │   └── search_queries/      # Task Level 5 gold standards
│   ├── baselines/               # Valentine + embedding baseline results
│   └── leaderboard.py           # Public leaderboard generation
│
├── sandbox/                     # EVOLVED from exec_apptainer_harmonia.sh
│   ├── apptainer.def            # Container definition
│   ├── launch.sh                # Launch script with SLURM integration
│   └── coding_agent_sandbox.sh  # NEW: Sandbox for frontier coding agent testing
│
├── experiments/                 # EVOLVED: Now includes sweep configs
│   ├── configs/                 # Per-experiment YAML configs
│   ├── sweeps/                  # NEW: Parameter sweep definitions
│   └── results/                 # Experiment outputs (gitignored)
│
├── scripts/
│   ├── build_geo_db.py          # NEW: Build GEO metadata database
│   ├── embed_geo.py             # NEW: Embed GEO descriptions for vector search
│   ├── run_benchmark.py         # NEW: Run full benchmark suite
│   └── generate_paper_figures.py # NEW: Generate all paper figures
│
└── paper/                       # NEW: Paper LaTeX source
    ├── figures/
    ├── tables/
    └── main.tex
```

### Key Architectural Changes (diff from current)

For each change, specify: what it replaces, why the change is needed, estimated effort, and priority (P1 = essential for first publication, P2 = strengthens first publication, P3 = stretch/second publication, P-Extra = future). **All components should be designed with clean interfaces from the start, even if only P1 components are fully implemented in the first 6 months.**

1. **model_factory.py** [P2]: Replace single-model assumption with per-phase model support. Enables testing different models for schema matching vs. value mapping within one experiment. Useful if the model-architecture interaction experiments (per Matchmaker's findings) are included. *Effort: Small. Risk: Low.*

2. **structured_output.py** [P2]: Add Pydantic validation for agent outputs (column_mapping.json, value_mapping.json) with retry-on-failure. Reduces hallucinated output failures. Low effort, high defensive value. *Effort: Small. Risk: Low.*

3. **search/ module** [P2 if search is in first paper; P3 if first paper focuses on harmonization only]: Full GEO search pipeline. Can be developed independently. The GEO database itself is P1 infrastructure regardless, as it provides the corpus for everything. *Effort: Large. Risk: Medium.*

4. **coding_agent.py** [P1]: Minimal coding agent with bash + read + write tools (no BDI-Kit). Essential for the "frontier coding agent baseline" comparison. *Effort: Medium. Risk: Low.*

5. **compositional.py** [P1]: Reimplement the Matchmaker compositional LM program (ColBERTv2 candidate retrieval + LLM reasoning candidates → refinement → MCQ confidence scoring with abstain) adapted for GDC harmonization. This is a key comparison architecture: a fixed multi-stage pipeline without an agent loop, representing the current SOTA for zero-shot schema matching. The paper provides Algorithm 2 and full prompt examples (Appendix C) for reimplementation. Also implement the DSPy bootstrapping optimization for this pipeline. *Effort: Medium (well-documented algorithm). Risk: Low.*

6. **benchmark/ directory** [P1]: The Gene Expression Omnibench. Gold standard tasks + evaluation code + leaderboard. **This is the most valuable code artifact.** *Effort: Large (mostly annotation work). Risk: Low.*

7. **sweep.py** [P1]: Automated parameter sweeps across models, architectures, and prompt variants. Currently this is done by manually generating SLURM job scripts. *Effort: Medium. Risk: Low.*

8. **comparison.py** [P1]: Statistical comparison utilities (McNemar, Wilcoxon, bootstrap CIs, Bonferroni correction). *Effort: Small. Risk: Very low.*

9. **multi_agent.py** [P3]: Multi-agent orchestration (hierarchical supervisor, fan-out/fan-in for N-table parallelism). The natural next step for N-table harmonization and end-to-end pipeline work. Design the interface now (P1) so the implementation plugs in cleanly later. *Effort: Large. Risk: Medium (complexity, but SRAgent provides a proven pattern).*

### What Should NOT Change

1. **Phoenix/OTel tracing** — Keep. It works and provides the observability needed.
2. **YAML experiment configs** — Keep. They enable reproducible experiments.
3. **Plotly Dash dashboard** — Keep. Extend for new experiment types.
4. **Apptainer sandboxing** — Keep. It provides the isolation needed.
5. **The two primary agent paradigms** (ReAct + BDI-Kit domain tools, and CodeAct) — Keep both. They are the core experimental conditions.
6. **The evaluation pipeline** — Keep and extend. `calculate_all_metrics()` is solid.

### Interfaces Between Components

Specify the data contracts between the search pipeline and the harmonization pipeline:

```python
@dataclass
class SearchResult:
    """Output of the search pipeline, input to harmonization."""
    query: str
    gse_ids: list[str]
    metadata: dict[str, GEOSeriesMetadata]  # Per-GSE metadata
    relevance_scores: dict[str, float]       # Per-GSE relevance score
    search_trace: dict                       # Full trace for observability

@dataclass  
class HarmonizationResult:
    """Output of the harmonization pipeline."""
    gse_id: str
    schema_mapping: dict[str, str]           # source_col → GDC_col
    value_mapping: dict[str, dict[str, str]] # col → {source_val → GDC_val}
    harmonized_table: pd.DataFrame           # Final harmonized data
    mapping_code: str                        # Deterministic Python code
    metrics: HarmonizationMetrics            # Auto-evaluated quality
    trace: dict                              # Full trace for observability
```

---

## ONE-PAGE EXECUTIVE SUMMARY

**Title**: *Gene Expression Omnibench: Benchmarking LLM-Based Metadata Harmonization for Omics Data*

**The problem**: Despite the availability of >250,000 omics datasets in repositories like GEO, finding and harmonizing their metadata for large-scale analyses remains a labor-intensive manual task. LLM-based tools promise automation, but there is no domain-specific benchmark, no systematic comparison of models and architectures, and no practical guidelines for omics researchers.

**What we will build**: (1) **Gene Expression Omnibench** — the first benchmark suite for omics metadata harmonization, comprising gold-standard tasks at five complexity levels (single-table to end-to-end search+harmonize); (2) A comprehensive comparison of classical methods (Valentine), embedding methods, LLM-based tools (LLMatch, Matchmaker, BDI-Kit), frontier models, local models, and frontier coding agents (Claude Code, Codex) on this benchmark, including a reimplementation of the current SOTA Matchmaker compositional pipeline adapted for the omics domain; (3) A taxonomy of failure modes with practical mitigation guidelines.

**The most important expected finding**: We expect to show that (a) LLM-based approaches significantly outperform classical and embedding-based methods on omics-specific metadata harmonization, but (b) the margin between a well-prompted frontier coding agent and a specialized multi-tool agent is smaller than expected, suggesting that context engineering matters more than tool architecture. We will also test whether Matchmaker's finding that compositional pipeline design compensates for weaker backbone models (GPT-3.5 Matchmaker ≈ GPT-4 ReMatch) holds in the omics domain — if so, this has major implications for budget-constrained labs using local models. We will quantify the quality gap between frontier and local models and identify the Pareto-optimal configurations on the cost-quality frontier.

**Why it matters**: This work provides the omics community with (a) a reusable benchmark for evaluating future harmonization tools, (b) empirical evidence for which LLM-based approaches work and which don't for their specific data, and (c) practical guidelines including: "for budget X, use model Y with approach Z to achieve quality W." The benchmark and evaluation framework will be publicly released.

---

## SEARCH QUERIES TO EXECUTE

Execute searches to fill any gaps from Reports A–D:

1. "omics metadata harmonization benchmark 2025 2026" — ensure no competing benchmark was published
2. "Gene Expression Omnibus automated curation 2025 2026" — any new GEO curation tools
3. "LLM data integration benchmark leaderboard" — existing leaderboards to learn from
4. "Claude Code data processing evaluation" — has anyone benchmarked coding agents for data tasks?
5. "six month research plan computational biology template" — research planning resources
6. "reproducibility package bioinformatics journal requirements" — what journals expect
7. "schema matching omics metadata GDC TCGA" — domain-specific prior work
8. "DSPy data integration prompt optimization" — DSPy for this specific task
9. "multi-agent LLM data processing empirical comparison" — empirical evidence on multi-agent value
10. "automated metadata curation bioinformatics 2025 2026" — the broader field

---

## CRITICAL REMINDERS FOR SYNTHESIS

- **Be honest about feasibility but do not discard ideas.** Six months for one researcher is limited, so clearly separate what is achievable (P1 + P2) from what stretches the timeline (P3) and what is future work (P-Extra). But P3 and P-Extra ideas should be fully articulated — this document serves as the master research plan for a multi-year line of work, not just the first paper.
- **The benchmark (Gene Expression Omnibench) is the primary contribution.** If the system results are mixed, the benchmark alone justifies publication. The benchmark should be designed from the start to support both P1 and P3/P-Extra experiments.
- **The frontier coding agent comparison is the most provocative finding.** If Claude Code in full-auto mode matches a specialized pipeline, that is a major result worth reporting honestly.
- **Connect P1 and P2 experiments to paper sections.** Every P1/P2 experiment should contribute directly to the first manuscript. P3 and P-Extra experiments should be connected to a second or third paper outline in the roadmap.
- **Quantitative results need statistical backing.** No result should be reported without confidence intervals.
- **The codebase architecture should serve the full vision, built incrementally.** Design the architecture for the complete system (search + harmonization + observability + benchmarking), but implement it in stages — P1 components first, with clean interfaces that P2/P3 components plug into. Over-engineering for the first paper is wasteful, but under-designing forces rewrites later.
- **Integrate findings from all four reports.** If Report A identifies a system worth comparing but Report D says the experiment is too time-consuming for P1, classify it as P2 or P3 with a concrete plan for when and how to run it.
- **Include the failure mode taxonomy.** This is a unique contribution that practitioners value highly — possibly more than the quantitative benchmarks.
- **P3 and P-Extra are not a graveyard.** The extended experiments (multi-agent architectures, end-to-end pipeline, DSPy optimization at scale, paper full-text integration, N-table harmonization) are often the most scientifically interesting. Present them with the same specificity as P1 — protocols, expected outcomes, dependencies, and estimated time — so they can be executed immediately after the first publication.
