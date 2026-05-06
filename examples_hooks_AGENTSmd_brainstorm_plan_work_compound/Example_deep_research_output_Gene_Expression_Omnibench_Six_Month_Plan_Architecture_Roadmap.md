# Gene Expression Omnibench: Six-Month Research Plan, Codebase Architecture, and Research Roadmap for LLM-Based Omics Metadata Harmonization

---

## Executive Summary

**Title:** *Gene Expression Omnibench: Benchmarking LLM-Based Metadata Harmonization for Omics Data*

**The problem.** Over 250,000 omics datasets in repositories like GEO remain difficult to find and harmonize for large-scale analyses. LLM-based tools promise automation, but no domain-specific benchmark exists, no systematic comparison of models and architectures has been conducted on omics metadata, and no practical guidelines exist for omics researchers choosing among the growing number of tools.

**What we will build.** (1) **Gene Expression Omnibench** — the first benchmark suite for omics metadata harmonization, comprising gold-standard tasks at five complexity levels (single-table schema matching through end-to-end search-and-harmonize); (2) a comprehensive comparison of classical methods (Valentine), embedding methods, LLM-based tools (Magneto, Matchmaker reimplementation, SCHEMORA, BDI-Kit), frontier models, local models, and frontier coding agents (Claude Code, Codex) on this benchmark; (3) a failure mode taxonomy with practical mitigation guidelines.

**What we expect to find.** LLM-based approaches will significantly outperform classical and embedding-based methods on omics-specific metadata, but the margin between a well-prompted frontier coding agent and a specialized multi-tool agent will be smaller than expected — suggesting context engineering matters more than tool architecture. We will test Matchmaker's finding that compositional pipeline design compensates for weaker backbone models in the omics domain, quantify the quality gap between frontier and local models, and identify Pareto-optimal configurations on the cost-quality frontier.

**Six-month plan at a glance.** 7 essential (P1) experiments form the irreducible core for a publishable paper: benchmark construction, Valentine baselines, frontier and local model screening, frontier coding agent baseline, Matchmaker reimplementation, and failure mode taxonomy. 16 important (P2) experiments strengthen the paper and are feasible within the timeline. 7 stretch (P3) experiments may spill to month 7-8 and feed a second publication. 3 aspirational (P-Extra) ideas are fully specified for future work.

**Target venues.** BioDMS Workshop at VLDB 2026 (stepping stone, May 15 deadline), VLDB 2027 Experiments, Analyses & Benchmarks track (primary, rolling deadlines), NeurIPS 2026 Evaluations & Datasets track (May 4/6 deadline — aggressive but possible for a position paper).

**Why it matters.** This work gives the omics community a reusable benchmark for evaluating future harmonization tools, empirical evidence for which approaches work on their specific data, and practical "for budget X, use model Y with approach Z to achieve quality W" guidelines. The benchmark and evaluation framework will be publicly released on HuggingFace with Croissant machine-readable metadata.

---

## Conceptual Overview

Metadata harmonization for omics data — mapping the heterogeneous free-text annotations that researchers attach to their Gene Expression Omnibus (GEO) datasets into controlled vocabularies like the Genomic Data Commons (GDC) schema — sits at a productive intersection of four active research areas: classical schema matching (25 years of algorithms, now well-benchmarked via Valentine), LLM-based data integration (rapid progress from F1=0.04 to HitRate@5=80% in three years, but only on clinical schemas), agentic AI systems (where the "simplicity vs. capability" tradeoff is fiercely debated), and biomedical informatics (where GEO's free-text metadata is measurably harder than other repositories, with 38 percentage points lower recall than BioSample under identical LLM conditions).

The core tension this plan navigates is between **comprehensiveness and feasibility**: a single researcher in six months cannot explore the full combinatorial space of 10+ models × 5+ architectures × 3+ prompt strategies × 5+ quantization levels × 5 benchmark complexity levels. The resolution is a four-tier priority system (P1 essential → P-Extra aspirational) with explicit go/no-go gates, ensuring that the first publication stands on the strongest experiments while the full research vision is preserved for subsequent work.

Four key insights from the prior research reports shape every decision in this plan. First, **pipeline architecture dominates model choice** — Matchmaker demonstrated GPT-3.5 with a well-designed compositional pipeline outperforms GPT-4 with a simple pipeline, implying the highest-ROI investment is pipeline design. Second, **multi-agent systems are the wrong default** for sequential reasoning tasks like schema matching, with empirical failure rates of 41-87% across frameworks and 39-70% performance degradation on sequential tasks. Third, **the benchmark is the primary contribution** — if system results are mixed, the benchmark alone justifies publication. Fourth, **the frontier coding agent comparison is the most provocative finding** — if Claude Code in full-auto mode matches a specialized pipeline, that reshapes the field's direction toward context engineering over tool development.

---

## DELIVERABLE 1: PRIORITIZED SIX-MONTH RESEARCH PLAN

### 1.1 Competitive Landscape and Strategic Positioning

Gap-filling searches across 10 queries confirm: **no published benchmark evaluates GEO-to-GDC metadata harmonization**. The closest existing resources are Magneto's GDC-SM benchmark (10 CPTAC datasets, generic schema matching, Zenodo DOI: 10.5281/zenodo.14963588) and LLMatch's SchemaNet (7 multi-table schema pairs, healthcare/finance, not omics-specific). Valentine's fabricated datasets are now widely criticized as too lexical — multiple 2025-2026 papers note they contain artificial patterns (e.g., "Gender"→"Ge") that inflate classical matcher scores.

**Converging threats to watch.** The Freire lab ecosystem (BDI-Kit, now published in Cell Patterns February 2026 + Magneto in PVLDB 2025 + Harmonia arXiv:2502.07132 + BDIViz in IEEE TVCG 2025) is the most mature platform. Their Harmonia paper explicitly identifies "Agent Evaluation & Benchmarks" as an open research direction — Gene Expression Omnibench fills exactly this gap. Elucidata's commercial multi-agent system (bioRxiv June 2025) claims 93% recall across 23 GEO metadata fields but has no public benchmark. h5adify (bioRxiv March 2026) demonstrates local LLM harmonization for single-cell AnnData, a closely related task.

**Two confirmed white-space opportunities.** First, no systematic evaluation of frontier coding agents (Claude Code, Codex CLI) on structured biomedical data processing exists — existing coding benchmarks (SWE-bench, Terminal-Bench) test software engineering, not data integration. Second, while Matchmaker validated DSPy's BootstrapFewShot for schema matching (+5% acc@1), nobody has applied DSPy's broader optimizer suite (MIPROv2, GEPA) to this task or to the omics domain. Both represent genuinely novel contribution axes.

**Venue timing.** NeurIPS 2026's newly renamed "Evaluations & Datasets Track" has abstract deadline May 4 and paper deadline May 6, 2026. The track now emphasizes "evaluation as a scientific object of study," aligning well with a benchmark submission. Requirements include HuggingFace/Dataverse hosting, Croissant machine-readable metadata, and double-blind review. VLDB 2027's EA&B track has rolling monthly deadlines — a safer primary target. The BioDMS Workshop at VLDB 2026 (May 15 deadline) provides an immediate stepping-stone opportunity for a 2-4 page position paper with preliminary results.

### 1.2 Experiment Inventory with Priority Scoring

Priority Score = (Yield × Risk × Novelty) / (6 − Simplicity). Each experiment is scored on Simplicity (1-5, higher = easier), Yield (1-5, higher = more paper content), Risk (1-5, higher = more certain to produce useful results), and Novelty (1-5, higher = more unprecedented). Priority classification follows: P1 = irreducible core for publishable paper; P2 = substantially strengthens paper, feasible in 6 months; P3 = stretch, may spill to months 7-8; P-Extra = aspirational future work.

**P1 Experiments (7) — The irreducible core.** These experiments, and only these, produce a publishable paper if nothing else gets done.

**B1: Single-table GDC gold standards** (Score=33.3). Construct 5-10 GEO metadata tables with expert-annotated mappings to GDC. Sources: Dou 2020 (existing), CPTAC studies with Li 2023 ground truth, 3-5 new GEO series spanning different cancer types and metadata complexity. Target ≥200 ground-truth column matches across 10+ tables for adequate statistical power (McNemar's test at power=0.80, α=0.05 can detect F1 differences of 0.10 with 100-200 instances). Require ≥3 annotators, target Cohen's κ ≥ 0.60. No dependencies. *This is the most important single experiment — everything else depends on it.*

**B5: Extend evaluation pipeline** (Score=7.5, but essential infrastructure). Extend `calculate_all_metrics()` to support the new benchmark format, adding value mapping metrics (exact match for enums, semantic similarity via NCIt for partial credit), cross-table consistency scores, and statistical comparison utilities. Depends on B1. Low novelty but zero-risk infrastructure.

**S1: Valentine baselines** (Score=15.0). Run all five Valentine matchers (COMA, Cupid, SimilarityFlooding, DistributionBased, JaccardLevenMatcher) on the omics benchmark. These establish the floor performance. Valentine is pip-installable; execution is straightforward. Depends on B1.

**S3: Frontier LLM screening** (Score=20.0). Run top-3 frontier models (Claude Sonnet 4.6, GPT-5-mini, Gemini 2.5 Flash) × 3 architectures (ReAct+tools, CodeAct, frontier coding agent) = 9 configurations × 3 runs = 27 experiments. This is the central model-architecture interaction test. Depends on B1, B5. ~50 API calls, ~$100-200.

**S4: Local LLM screening** (Score=20.0). Run top-4 mid-range local models (Qwen3.5-35B-A3B, Gemma 4 26B-A4B, Gemma 4 31B dense, Qwen3.5-27B dense) × best architecture from S3 = 12-16 configurations × 3 runs. Tests the frontier-local quality gap. Updated model roster reflects Gemma 4 (released April 2, 2026) and Qwen 3.5 (February-March 2026). Depends on B1, B5. Requires vLLM on HPC GPU.

**S6: Frontier coding agent baseline** (Score=25.0). Run Claude Code headless (`claude -p "prompt" --output-format json --dangerously-skip-permissions`) and Codex CLI (`codex exec --full-auto --json`) on the same benchmark tasks, given only source CSV, target GDC schema, BDI-Kit as installed library, and a well-crafted CLAUDE.md with 5-10 difficult mapping examples. This is the "Kapoor test" — if frontier coding agents achieve ≥85% column mapping accuracy at <$5 per dataset, all bespoke pipeline work is premature optimization. **No published study has evaluated coding agents on structured biomedical data processing**, making this a genuinely novel baseline. Depends on B1.

**S7: Reimplement Matchmaker** (Score=25.0). Reimplement Matchmaker's compositional LM program (ColBERTv2 candidate retrieval + dual candidate generation [semantic + reasoning] → LLM refinement → MCQ confidence scoring with abstain option) adapted for GDC harmonization. Paper provides Algorithm 2 and full prompt examples (Appendix C). Also implement DSPy BootstrapFewShot optimization for this pipeline (+5% acc@1 validated in original paper). No code published, but well-documented algorithm. This is the current SOTA for zero-shot LLM-based schema matching. Depends on B1. Effort: medium (2 weeks).

**E2: Failure mode taxonomy** (Score=30.0). Document failure modes from all experiments using the existing 20-class taxonomy across 6 categories (Infrastructure, Model Config, LLM Behavioral, Data/Config, Output, Diagnostic). Extend with GDC-specific failure modes. This is a unique contribution that practitioners value highly — possibly more than quantitative benchmarks. Begins in Month 1, completes in Month 5. Depends on S3, S4.

**P2 Experiments (16) — Strengthen the paper.** Aim to complete all; can be deprioritized if P1 takes longer.

B2 (two-table gold standards), B4 (search query gold standards), S2 (embedding model comparison: MPNet, BGE, SapBERT, MedCPT, PubMedBERT), S5 (small local LLMs: Qwen3.5-9B, Gemma 4 E4B, Mistral Nemo), S7b (LLMatch/Magneto comparison if code available), S8 (context content ablation per ConStruM: vary sample values 0/5/10/20, schema representation, ontology access, and test Matchmaker's dual candidate generation insight), S9 (temperature and reasoning settings ablation), V1 (value mapping comparison: LLM vs. dictionary lookup vs. ontology matching), M1 (two-table harmonization), P1opt (manual prompt optimization from error analysis), R1 (BM25 over GEO SQLite FTS5), R2 (dense embedding retrieval for GEO), R3 (hybrid BM25+dense with RRF), A1 (per-agent model configuration), A2 (structured output validation with Pydantic), A4 (quantization sweep Q4/Q5/Q6/Q8/F16).

**P3 Experiments (7) — Stretch goals.** Fully specified and ready to execute, but may spill to months 7-8.

B3 (N-table gold standard from CPTAC 10-table set), V2 (constrained generation for value mapping), M2 (N-table harmonization), M3 (multi-agent vs. single-agent for N-table), P2opt (DSPy optimization with MIPROv2/GEPA), R4 (LLM reranking for search), E1 (end-to-end search→harmonize pipeline).

**P-Extra Experiments (3) — Future work.** R5 (paper full-text embedding and retrieval), R6 (agentic multi-step search), A3 (streaming progress display).

### 1.3 Month-by-Month Timeline

#### Month 1: Foundation, Benchmark Construction, and Quick Wins

**Weeks 1-2: Benchmark gold standard construction.** Execute B1 (5-10 single-table gold standards) and B5 (evaluation pipeline extension). Source tables from: Dou 2020 (already available), CPTAC studies with Li 2023 ground truth (already available), and 3-5 new GEO series representing different cancer types (breast, lung, colorectal) and metadata complexity levels (structured vs. free-text heavy). Simultaneously begin B4 (10-15 search queries with semi-gold-standard GEO ID sets using existing lab classifications). Start GEO database construction as a background process — this requires downloading and parsing GEO SOFT files, building the SQLite+FTS5 database per the final_implementation_plan_GEO_db.md specification.

**Deliverables:** Benchmark dataset v1.0 (≥5 tables, ≥150 ground-truth column matches), evaluation pipeline v2.0 supporting schema matching and value mapping metrics.

**Go/no-go:** If gold standards cannot be constructed for ≥5 tables by end of week 2, narrow to Dou 2020 + CPTAC tables only (≥4 tables, sufficient for initial experiments). Annotator recruitment and training should begin before Month 1.

**Weeks 3-4: Classical baselines + frontier model screening.** Execute S1 (Valentine baselines — `pip install valentine`, run all 5 matchers on benchmark), S3 (frontier LLM screening — 9 configurations × 3 runs = 27 experiments), and S6 (Claude Code + Codex full-auto baseline). Begin E2 (failure mode documentation from each run). The S6 experiment is the single most important architectural decision point: if a frontier coding agent with only a CLAUDE.md file matches or exceeds a specialized agent with domain tools, this fundamentally redirects the research.

**Deliverables:** Valentine baseline results, frontier model results across 3 architectures, frontier coding agent baseline, initial failure mode observations.

**Person-hours:** ~80-100. **Compute:** ~50 frontier API calls (~$100-200). **GPU:** Negligible (all frontier API).

**Go/no-go decision (end of Month 1):** Two binary questions determine the paper's narrative. (1) Do LLM-based approaches outperform Valentine baselines? If not, investigate why — the 38-point GEO recall gap identified by "Toward Total Recall" suggests GEO-specific challenges that may need targeted context engineering. (2) Does the bespoke pipeline outperform frontier coding agents? If not, the paper becomes "off-the-shelf coding agents match or exceed specialized tools for omics metadata harmonization" — arguably more impactful than the reverse finding.

#### Month 2: Local Model Screening and Architecture Comparison

**Weeks 5-6: Local model experiments.** Execute S4 (4 mid-range local models × best architecture from Month 1, using vLLM on SLURM/Apptainer). The model roster has been updated to reflect the latest releases: Qwen3.5-35B-A3B (MoE, 3B active, Apache 2.0), Gemma 4 26B-A4B (MoE, ~4B active, Apache 2.0 — released April 2, 2026), Gemma 4 31B dense, and Qwen3.5-27B dense. Execute S5 (3 small local models: Qwen3.5-9B, Gemma 4 E4B, Mistral Nemo 12B). Execute A4 (quantization sweep: Q4_K_M/Q5_K_M/Q6_K/Q8/F16 for best local model). This quantization experiment fills a confirmed research gap — no published work isolates quantization effects on schema matching accuracy.

**Weeks 7-8: Architecture deep-dive.** Execute S2 (embedding model comparison: MPNet, BGE-large-en-v1.5, SapBERT, MedCPT, PubMedBERT on benchmark), S8 (context content ablation with best frontier model), and begin S7 (Matchmaker reimplementation — allocate 2 weeks, with fallback to reporting reproduction challenges). Attempt S7b (LLMatch/Magneto comparison) if code is available.

**Deliverables:** Local vs. frontier comparison table, quantization impact curves, architecture comparison results, context ablation results, embedding baselines, Matchmaker reimplementation (or documented attempt).

**Go/no-go decision (end of Month 2):** Which architecture wins — ReAct+tools, CodeAct, frontier coding agent, or Matchmaker compositional pipeline? This determines the focus for the remaining months.

#### Month 3: Value Mapping, Multi-Table, and Search Pipeline

**Weeks 9-10:** Execute V1 (value mapping comparison), B2 (two-table gold standards), M1 (two-table harmonization), and P1opt (manual prompt optimization based on Month 1-2 error analysis). Value mapping is the harder unsolved half of harmonization — the 79-point gap between in-dictionary (96%) and out-of-dictionary (17%) accuracy from Verbitsky et al. underscores the challenge.

**Weeks 11-12:** Execute R1 (BM25 search over GEO FTS5 database — requires GEO database to be complete), R2 (embed GEO Series descriptions with best model from S2), R3 (hybrid retrieval with RRF), and test on gold-standard queries from B4.

**Deliverables:** Value mapping results, two-table harmonization results, search pipeline v1, retrieval evaluation.

#### Month 4: Ablations and Stretch Goals

**Weeks 13-14:** Execute S9 (temperature ablation), complete S8 (context ablation analysis), A1 (per-agent model configuration), A2 (structured output validation). These are relatively low-effort experiments that fill out the ablation section of the paper.

**Weeks 15-16:** Begin P3 stretch goals: M2 (N-table harmonization if B3 gold standard is complete), R4 (LLM reranking for search), P2opt (DSPy optimization if benchmark ≥20 tables). These experiments have lower risk scores and may not produce results, but are worth attempting.

#### Month 5: End-to-End and Comprehensive Analysis

**Weeks 17-18:** Execute E1 (end-to-end search→harmonize on gold-standard queries, P3 stretch), complete E2 (finalize failure mode taxonomy with examples from all experiments, P1). The failure taxonomy is one of the paper's unique contributions — spend the time to make it comprehensive, with concrete examples and frequencies from the actual benchmark runs.

**Weeks 19-20:** Statistical analysis of all results: McNemar's exact test for pairwise binary comparisons (correct/incorrect per column), Cochran's Q → pairwise McNemar with Holm-Bonferroni for >2 configurations, Wilcoxon signed-rank across datasets, Friedman test with Nemenyi post-hoc for all-system comparison. Report bootstrap BCa 95% CIs and Cliff's δ effect sizes throughout. Generate cost-quality Pareto frontier plots, failure mode distributions, and all paper figures.

#### Month 6: Paper Writing and Reproducibility

**Weeks 21-22:** Draft paper: Introduction (revise with concrete results), Methods (benchmark construction, experimental setup, evaluation metrics), Results (schema matching comparison, architecture comparison, local vs. frontier, search pipeline, end-to-end), Discussion (failure modes, practical recommendations, limitations). Target ~10-12 pages for VLDB EA&B or NeurIPS E&D format.

**Weeks 23-24:** Reproducibility package: code on GitHub with MIT/Apache 2.0 license, experiment configs (YAML), Docker/Apptainer images, benchmark data on HuggingFace with Croissant metadata. Public release of Gene Expression Omnibench. Internal review and revision. If targeting NeurIPS 2026, the paper must be ready by May 4-6 — this requires compressing the timeline by approximately 1 month, focusing solely on P1 experiments.

### 1.4 Contingency Plans and Go/No-Go Decision Framework

**If benchmark gold standard construction takes longer than 2 weeks:** Use only Dou 2020 + CPTAC tables with Li 2023 ground truth (already available). This gives ≥4 tables with ≥100 ground-truth column matches — sufficient for initial experiments and adequate statistical power to detect F1 differences of 0.10.

**If frontier coding agents outperform the bespoke pipeline:** This is itself a major finding. The paper becomes: "Off-the-shelf coding agents match or exceed specialized tools for omics metadata harmonization — implications for the field." The narrative shifts from "our pipeline is better" to "context engineering (the CLAUDE.md file) matters more than tool architecture." This is arguably more impactful and provocative, since it implies the field should invest in better prompts and context curation rather than more complex agent frameworks.

**If local models perform poorly relative to frontier:** Focus the paper on the frontier model comparison + failure taxonomy + practical guidelines. The local model results become a section quantifying the quality gap and its implications for budget-constrained labs. Report the Pareto frontier with cost-quality tradeoffs: "if your budget is $X per harmonization, use model Y with architecture Z to achieve quality W." This is actionable information regardless of whether local models close the gap.

**If GEO database construction is not complete by Month 3:** Use a subset of GEO (e.g., all human cancer studies, ~50K series) for the search experiments, and report results as preliminary. The full database can be completed post-publication. Alternatively, deprioritize search experiments (R1-R3) from P2 to P3 and strengthen the harmonization-focused paper.

**If LLMatch/Magneto code is not available or reproducible:** Report this as a limitation. Run Valentine baselines + embedding baselines as comparison points. Cite Magneto and LLMatch's published results on their respective benchmarks and note the comparison is limited by code availability — this is itself a useful data point about reproducibility in the field.

**If Matchmaker reimplementation takes longer than 2 weeks:** Implement a simplified version capturing the core insights: dual candidate generation (semantic retrieval + LLM reasoning) with MCQ confidence scoring. Omit ColBERTv2 integration and DSPy bootstrapping for the first pass. The simplified version still tests the compositional pipeline hypothesis.

**If NeurIPS deadline (May 4-6) is a target:** Compress the timeline to 4 months of experiments + 1 month of writing. Execute only P1 experiments. Submit results on 5-7 tables with frontier models, coding agents, and Valentine baselines. This is tight but achievable if benchmark construction begins immediately.

**Pivotal go/no-go decisions:**

| Decision point | Timing | Question | If YES | If NO |
|---|---|---|---|---|
| End of Month 1 | Week 4 | Do LLMs outperform Valentine? | Proceed with full plan | Investigate GEO-specific challenges; may need domain-specific context engineering |
| End of Month 1 | Week 4 | Does bespoke pipeline outperform coding agents? | Develop bespoke pipeline further | Shift narrative to coding agent finding |
| End of Month 2 | Week 8 | Is best local model within 10% of frontier? | Local models become a central result | Report quality gap; focus on frontier + cost analysis |
| End of Month 3 | Week 12 | Is search pipeline producing useful results? | Include search in paper | Defer search to Publication 2 |
| End of Month 4 | Week 16 | Can P3 experiments be completed in remaining time? | Execute stretch goals | Focus on polishing P1+P2 results |

### 1.5 Resource Requirements

| Resource | Quantity | Estimated Cost | Notes |
|---|---|---|---|
| GPU compute (A100/A40) | ~200 GPU-hours total | Free (institutional HPC) | vLLM inference for local models, embedding computation |
| Frontier model API costs | ~500-1000 API calls | ~$200-500 | Claude Sonnet 4.6 ($3/$15 per M tokens), GPT-5-mini, Gemini Flash |
| Claude Code / Codex CLI | ~50-100 invocations | ~$50-150 | Frontier coding agent baseline (S6) |
| Storage for GEO database + embeddings | ~200 GB | Free (HPC storage) | SQLite DB (~50GB) + vector embeddings (~1GB) + papers (optional, ~100GB) |
| Expert annotation time for gold standards | ~40-60 person-hours | In-kind (lab members) | ≥3 annotators for B1, ≥2 for B2, B4 |
| Paper full-text downloads (P-Extra) | ~150K papers | ~100 GB storage + download time | Optional, deferred to Publication 2 |
| HuggingFace hosting | Benchmark dataset + Croissant metadata | Free (academic) | Required for NeurIPS/VLDB submission |

**Total estimated cash cost: $250-650.** The primary constraint is researcher time (1 person, 6 months), not compute or API costs. The largest hidden cost is expert annotation time for gold standards (B1, B2, B4), which requires coordinating with lab members who have GDC domain expertise.

---

## DELIVERABLE 2: PROPOSED CODEBASE ARCHITECTURE

### 2.1 Current Architecture Assessment

The current research fork (Harmonia) is a heavily extended version of the published BDI-Kit/Harmonia system (Lopez et al., Patterns 2026; Santos et al., arXiv 2025). It provides a working metadata harmonization agent with two primary paradigms: (1) ReAct + BDI-Kit domain tools (5 tools: `match_schema`, `rank_schema_matches`, `match_values`, `materialize_mapping`, `get_gdc_acceptable_values`) via the Archytas framework, and (2) true CodeAct where the LLM writes executable Python in markdown fences, executed via the Beaker kernel. The system includes Apptainer sandboxing for HPC, Phoenix/OTel tracing with OpenInference semantic conventions, a Plotly Dash dashboard with 8 tabs (overview, metrics, failure analysis, error analysis, trace explorer, token cost, comparison, activity log), YAML-configured experiments, a 20-class failure taxonomy across 6 categories, and an evaluation pipeline centered on `calculate_all_metrics()`.

**Strengths of the current architecture.** The dual-paradigm design (ReAct vs. CodeAct) is itself an experimental variable worth preserving. Phoenix/OTel tracing provides the observability needed for diagnosing agent failures. YAML experiment configs enable reproducible experiments. The Apptainer sandboxing works on institutional HPC. The failure taxonomy is a research asset.

**Gaps the v2 architecture must address.** (1) No support for the frontier coding agent paradigm (Claude Code / Codex headless). (2) No compositional LM program architecture (Matchmaker pattern). (3) No benchmark infrastructure — gold standards, batch evaluation, statistical comparison. (4) No parameter sweep automation — experiments are launched individually. (5) No search pipeline. (6) No structured output validation (Pydantic). (7) No per-phase model configuration (e.g., cheap model for candidate generation, expensive model for reranking). (8) No prompt versioning system.

### 2.2 Proposed Architecture: geo-harmonizer v2

The proposed architecture is designed for the complete vision (search + harmonization + observability + benchmark) but built incrementally. P1 components create foundations that P2/P3 naturally extend. Every boundary has a clean interface.

```
geo-harmonizer/
├── src/
│   ├── core/                        # Shared infrastructure
│   │   ├── model_factory.py         # [P2] Multi-model support (SRAgent Pattern 2)
│   │   ├── structured_output.py     # [P2] Pydantic validation + retry (SRAgent Pattern 3)
│   │   ├── tracing.py               # [KEEP] Extended for multi-agent traces
│   │   ├── config.py                # [EVOLVE] Phase-specific model/temperature overrides
│   │   └── caching.py              # [P1] SHA-256 hash-keyed LLM call caching
│   │
│   ├── search/                      # [P2/P3] GEO search pipeline
│   │   ├── geo_database/            # [P2] SQLite + FTS5 (from geo_metadata_db plan)
│   │   ├── embeddings/              # [P2] Vector store (Qdrant) for GEO descriptions
│   │   ├── retrieval.py             # [P2] Hybrid retrieval (BM25 + dense + reranking)
│   │   ├── query_expansion.py       # [P3] LLM-based ontology-guided expansion
│   │   └── evaluation.py            # [P3] Search-specific metrics (Recall@K, NDCG)
│   │
│   ├── harmonization/               # EVOLVED from current src/
│   │   ├── agents/
│   │   │   ├── bdikit_agent.py      # [KEEP] ReAct + domain tools
│   │   │   ├── codeact_agent.py     # [KEEP] True CodeAct
│   │   │   ├── coding_agent.py      # [P1] Minimal coding agent (bash+read+write)
│   │   │   ├── compositional.py     # [P1] Matchmaker-style fixed pipeline
│   │   │   └── multi_agent.py       # [P3] Hierarchical multi-agent (interface now)
│   │   ├── prompts/                 # [EVOLVE] Versioned Jinja2 templates
│   │   ├── tools/                   # [KEEP] BDI-Kit tools + extensions
│   │   └── materialize.py           # [KEEP] Deterministic mapping code generator
│   │
│   ├── evaluation/                  # EVOLVED from current
│   │   ├── metrics.py               # [EVOLVE] Schema matching + value mapping metrics
│   │   ├── benchmark.py             # [P1] Benchmark task runner
│   │   ├── comparison.py            # [P1] Statistical comparison (McNemar, bootstrap)
│   │   └── visualization.py         # [P2] Publication-quality plots
│   │
│   ├── dashboard/                   # [KEEP+EXTEND] Plotly Dash UI
│   │
│   └── experiment/                  # EVOLVED from src/automation/
│       ├── runner.py                # [EVOLVE] Multi-config support
│       ├── sweep.py                 # [P1] Automated parameter sweeps
│       └── analysis.py              # [P2] Post-experiment statistical analysis
│
├── benchmark/                       # [P1] Gene Expression Omnibench
│   ├── tasks/
│   │   ├── single_table_gdc/        # [P1] Task Levels 1-2 gold standards
│   │   ├── two_table/               # [P2] Task Level 3 gold standards
│   │   ├── n_table/                 # [P3] Task Level 4 gold standards
│   │   └── search_queries/          # [P2] Task Level 5 gold standards
│   ├── baselines/                   # [P1] Valentine + embedding baseline results
│   └── leaderboard.py              # [P2] Public leaderboard generation
│
├── sandbox/                         # EVOLVED
│   ├── apptainer.def               # [KEEP] Container definition
│   ├── launch.sh                    # [KEEP] SLURM integration
│   └── coding_agent_sandbox.sh     # [P1] Sandbox for coding agent testing
│
├── experiments/                     # EVOLVED
│   ├── configs/                     # Per-experiment YAML configs
│   ├── sweeps/                      # [P1] Parameter sweep definitions
│   └── results/                     # Experiment outputs (gitignored)
│
├── scripts/
│   ├── build_geo_db.py              # [P2] Build GEO metadata database
│   ├── embed_geo.py                 # [P2] Embed GEO descriptions
│   ├── run_benchmark.py             # [P1] Run full benchmark suite
│   └── generate_paper_figures.py    # [P2] Generate all paper figures
│
└── paper/                           # [Month 6] LaTeX source
    ├── figures/
    ├── tables/
    └── main.tex
```

### 2.3 Key Architectural Changes with Priority Markers

**1. coding_agent.py [P1].** A minimal coding agent with only bash, read, write, and edit tools — no BDI-Kit domain tools. This is the wrapper for running Claude Code headless and Codex CLI as experimental conditions. Implementation: a thin shell that launches the agent process, captures structured JSON output, and logs to Phoenix/OTel. The key design decision is that this agent gets the same information as the bespoke agents (source table, GDC schema, data samples) but no domain-specific tools — it must figure out the approach from scratch. *Replaces: nothing (new component). Effort: small (2-3 days). Risk: very low.*

**2. compositional.py [P1].** Reimplementation of Matchmaker's three-stage pipeline: (i) dual candidate generation — ColBERTv2 (or a cross-encoder fallback) retrieval combined with LLM reasoning-based candidates; (ii) LLM refinement — narrows combined candidate set; (iii) MCQ confidence scoring with an abstain option. Also implements DSPy BootstrapFewShot optimization for each stage. This is a fixed pipeline (no agent loop), making it deterministic in structure though not in LLM outputs. Each stage is independently optimizable. *Replaces: nothing (new paradigm). Effort: medium (2 weeks). Risk: low — Algorithm 2 + Appendix C prompts in paper provide sufficient detail.*

**3. benchmark/ directory [P1].** The Gene Expression Omnibench. Gold standard tasks in standardized JSON format, evaluation code that computes all metrics, and baseline results for reference. The task format is a `BenchmarkTask` dataclass with task_id, complexity level (1-5), source table path, target schema path, gold standard mappings, and metadata. The evaluation code wraps `calculate_all_metrics()` with additional value mapping metrics and cross-table consistency scores. *Replaces: ad hoc evaluation. Effort: large (mostly annotation work, ~40-60 person-hours). Risk: low.*

**4. sweep.py [P1].** Automated parameter sweeps across models, architectures, prompt variants, and quantization levels. Generates SLURM job arrays from sweep definition YAML files. Manages experiment namespacing, result collection, and parallel execution. Currently this is done by manually creating SLURM scripts. *Replaces: manual SLURM script generation. Effort: medium (1 week). Risk: low.*

**5. comparison.py [P1].** Statistical comparison utilities: McNemar's exact test for pairwise binary comparisons, Cochran's Q for >2 configurations, Wilcoxon signed-rank for continuous metrics, Friedman test with Nemenyi post-hoc, bootstrap BCa 95% confidence intervals, Cliff's δ effect sizes, and Bonferroni/Holm correction for multiple comparisons. All implemented using scipy.stats and custom bootstrap code. *Replaces: nothing (new). Effort: small (2-3 days). Risk: very low.*

**6. caching.py [P1].** Exact-match LLM call caching using SHA-256 hash of (prompt string + model ID + generation parameters) as cache key. Stores first successful response in SQLite. Makes the application deterministic at the interface boundary. Integrates with tracing so cached calls are marked as such in Phoenix. *Replaces: nothing (new). Effort: small (1-2 days). Risk: very low.*

**7. model_factory.py [P2].** Per-phase model support via SRAgent's Pattern 2. Enables testing different models for candidate generation vs. reranking vs. value mapping within a single experiment run (e.g., Qwen3.5-9B for cheap candidate generation, Claude Sonnet for expensive reranking). Configuration via YAML: `phases: {candidates: "qwen3.5-9b", reranking: "claude-sonnet-4.6", value_mapping: "gemma-4-26b"}`. *Replaces: single-model assumption. Effort: small. Risk: low.*

**8. structured_output.py [P2].** Pydantic validation for agent outputs (column_mapping.json, value_mapping.json) with automatic retry on validation failure — SRAgent's Pattern 3. Reduces hallucinated output failures. The retry mechanism re-prompts with the validation error message, giving the LLM a chance to self-correct. Maximum 3 retries before falling back to partial results. *Replaces: nothing (defensive addition). Effort: small. Risk: low.*

**9. search/ module [P2 for database, P3 for full pipeline].** Full GEO search pipeline: SQLite+FTS5 for BM25, Qdrant for dense retrieval, hybrid RRF fusion, cross-encoder reranking. Can be developed independently of the harmonization pipeline. The GEO database itself (P2 infrastructure) is needed regardless of whether search enters the first paper — it provides the corpus metadata for benchmark construction and future work. *Replaces: nothing (new subsystem). Effort: large. Risk: medium.*

**10. multi_agent.py [P3 — design interface now, implement later].** Hierarchical multi-agent orchestration for N-table harmonization: supervisor agent delegates to parallel harmonization agents (one per table), then a merge agent checks cross-table consistency. Uses LangGraph's `Send()` API for fan-out. Interface defined now so P1/P2 single-agent work feeds cleanly into P3 multi-agent experiments. *Replaces: nothing. Effort: large. Risk: medium.*

### 2.4 Component Interfaces and Data Contracts

The architecture defines four critical interface boundaries. Strict typing via Python dataclasses ensures components can be developed and tested independently.

**Benchmark → Evaluation interface:**

```python
@dataclass
class BenchmarkTask:
    """A single evaluation task in Gene Expression Omnibench."""
    task_id: str                          # e.g., "L1_GSE12345_gdc"
    level: int                            # 1-5 (single-table to end-to-end)
    source_table: pd.DataFrame            # Raw GEO metadata table
    target_schema: dict                   # GDC schema subset (relevant nodes)
    gold_schema_mapping: dict[str, str]   # source_col → GDC_property
    gold_value_mapping: dict[str, dict]   # col → {source_val → GDC_val} (Level 2+)
    metadata: dict                        # GSE ID, organism, platform, cancer type
    difficulty_tags: list[str]            # e.g., ["free_text_heavy", "ambiguous_columns"]
```

**Search → Harmonization interface (the handoff contract):**

```python
@dataclass
class SearchResult:
    """Output of the search pipeline, input to harmonization."""
    query: str
    gse_ids: list[str]
    metadata: dict[str, GEOSeriesMetadata]  # Per-GSE structured metadata
    relevance_scores: dict[str, float]       # Per-GSE calibrated relevance
    match_evidence: dict[str, list[str]]     # Per-GSE: which query terms matched
    search_trace: dict                       # Full trace for observability
```

**Harmonization → Evaluation interface:**

```python
@dataclass
class HarmonizationResult:
    """Output of any harmonization agent/pipeline."""
    task_id: str
    agent_type: str                        # "react_bdikit", "codeact", "coding_agent",
                                           # "compositional", "multi_agent"
    schema_mapping: dict[str, str]         # source_col → GDC_property
    value_mapping: dict[str, dict[str, str]]  # col → {source_val → GDC_val}
    confidence_scores: dict[str, float]    # Per-mapping confidence
    harmonized_table: pd.DataFrame | None  # Final harmonized data (optional)
    mapping_code: str | None               # Deterministic Python code (materialize)
    metrics: HarmonizationMetrics          # Auto-evaluated quality
    trace: dict                            # Full trace for observability
    cost_usd: float                        # Total API cost for this run
    wall_time_seconds: float               # End-to-end wall time
    failure_modes: list[str]               # Detected failure taxonomy classes
```

**Experiment → Statistical Comparison interface:**

```python
@dataclass
class ExperimentSuite:
    """A collection of runs across configurations for statistical comparison."""
    benchmark_tasks: list[BenchmarkTask]
    configurations: list[dict]             # Model × architecture × prompt combos
    results: dict[str, list[HarmonizationResult]]  # config_id → [runs]
    
    def compare_pairwise(self, config_a: str, config_b: str) -> PairwiseComparison:
        """McNemar's test + Cliff's δ + bootstrap CIs."""
        ...
    
    def compare_all(self) -> MultiComparison:
        """Friedman + Nemenyi post-hoc with Holm-Bonferroni correction."""
        ...
    
    def pareto_frontier(self, x='cost_usd', y='f1_score') -> list[str]:
        """Identify Pareto-optimal configurations."""
        ...
```

These contracts ensure that any agent implementation — whether ReAct, CodeAct, frontier coding agent, Matchmaker pipeline, or future multi-agent — produces outputs in the same format, enabling apples-to-apples comparison. The `agent_type` field enables architecture-specific analysis without requiring architecture-specific evaluation code.

### 2.5 What Should Not Change

Six components of the current architecture are battle-tested and should be preserved:

**Phoenix/OTel tracing.** The existing span hierarchy (AGENT → CHAIN → LLM → TOOL) with OpenInference semantic conventions works. Extend for multi-agent traces by propagating Trace IDs across agent boundaries and adding descriptive span naming (`schema_matcher:gdc_column_match` rather than generic `tool_call`). The 20-class failure taxonomy maps to span events with structured attributes (`failure.taxonomy_class`, `failure.agent_id`, `failure.recovery_attempted`).

**YAML experiment configs.** These enable reproducible experiments and are the natural format for sweep definitions. Extend to support quantization level, model-per-phase configuration, and prompt version references. Each experiment run should produce an immutable config snapshot alongside results.

**Plotly Dash dashboard.** The 8-tab structure provides the experiment analysis infrastructure needed. Extend with: a search pipeline tab (for R1-R3 evaluation), a statistical comparison tab (for comparison.py output visualization), and multi-agent trace views (for P3 experiments). Do not replace with a different framework.

**Apptainer sandboxing.** This is a hard requirement for HPC environments. The existing `.sif` image with Python 3.11, litellm, and BDI-Kit 0.9.0 works. Add a separate sandbox definition for frontier coding agent testing (`coding_agent_sandbox.sh`) that includes Claude CLI / Codex CLI and outbound HTTPS access.

**The two primary agent paradigms (ReAct + BDI-Kit tools, and CodeAct).** These are core experimental conditions, not implementation details. Both must be preserved as-is so the v2 experiments can be directly compared with existing results. New paradigms (coding agent, compositional) are additive.

**The evaluation pipeline.** `calculate_all_metrics()` is solid. Extend for value mapping metrics (exact match for enums, Wu-Palmer semantic similarity via NCIt for partial credit, BLEU/CER for string fields) and cross-table consistency scores (percentage of semantically equivalent source columns receiving identical target mappings). Do not rewrite — build on the existing Pydantic schemas (metrics.json v1.1).

---

## DELIVERABLE 3: RESEARCH ROADMAP BEYOND SIX MONTHS

### 3.1 Publication 2: Search Pipeline and End-to-End Evaluation (Months 7-12)

**Research question.** Can a GEO-specific RAG pipeline surface 80%+ of relevant studies for a given omics-data search query, and does the combination of search + harmonization produce usable harmonized datasets from open-ended biological queries?

**Experiments.** This publication picks up P2 search experiments (R1-R3, already started) and adds the deferred P3 experiments: R4 (LLM reranking — cross-encoder on top-100 candidates), R5 (paper full-text embedding and retrieval, with section-aware chunking at 100-200 tokens for Methods/Results), R6 (agentic multi-step search with Adaptive RAG routing for query complexity), and E1 (end-to-end search→harmonize pipeline on gold-standard queries from B4, expanded to 30-50 queries). The search evaluation framework uses Recall@K as the primary metric (Recall@100 ≥ 0.80 minimum, ≥ 0.85 target), with NDCG@10 for ranking quality and cascaded evaluation decomposing end-to-end success as P(search finds study) × P(study is processable) × P(harmonization succeeds) × P(data is usable).

**Infrastructure.** The GEO database (SQLite + FTS5, started as background task in Month 1) should be complete by Month 7. Qdrant deployed via Apptainer for dense retrieval. Embedding models from S2 results inform the choice between MedCPT, BMRETRIEVER-410M, and BGE-large. Ontology-guided query expansion using UMLS/MeSH/DOID following the BMQExpander approach (up to 22% NDCG improvement reported). Paper full-text integration via GROBID parsing of PMC articles citing GEO accessions (~47,000 articles available).

**Estimated effort.** 4-6 months for one researcher. The search pipeline is a largely independent subsystem — development can overlap with Publication 1 revisions. The main bottleneck is gold-standard query construction (B4 expansion) and paper full-text downloading/parsing.

**Expected outcome.** Hybrid BM25 + dense retrieval with ontology expansion will achieve Recall@100 of 0.80-0.90 (based on Report B estimates), a 15-30% improvement over keyword search alone. Paper full-text integration will add another 5-10% recall for queries whose answers are implicit in methodology descriptions. The end-to-end pipeline will successfully harmonize 60-70% of retrieved studies, with the remainder failing due to metadata quality issues (missing columns, inconsistent formatting, non-standard terminology).

**Target venue.** Bioinformatics (Oxford), Nucleic Acids Research (database issue), or CIKM 2027. A systems paper emphasizing the search pipeline architecture with end-to-end evaluation results.

### 3.2 Publication 3: Multi-Agent and N-Table Harmonization (Months 12-18)

**Research question.** How should harmonization scale to multi-table datasets (5-10 tables from the same study collection), and do multi-agent architectures justify their coordination overhead compared to sequential single-agent processing?

**Experiments.** This publication centers on the P3 experiments: B3 (N-table gold standard from CPTAC 10-table set with Li 2023 ground truth), M2 (N-table harmonization with best single-table configuration), M3 (multi-agent vs. single-agent for N-table — fan-out parallel processing via LangGraph `Send()`, hierarchical supervisor pattern, and sequential single-agent as control), P2opt (full DSPy optimization with MIPROv2 and GEPA optimizers, enabled by the larger training set from Publications 1-2 combined), and V2 (constrained generation for value mapping using llama.cpp GBNF grammars or vLLM structured output).

Additional experiments for this publication: (a) RLM (Recursive Language Model) pattern for processing datasets that exceed practical context limits — load source data and GDC schema as Python variables, partition columns into semantic groups via code, process each group with recursive sub-LM calls (Zhang et al., arXiv:2512.24601 demonstrated 34+ accuracy point improvements on OOLONG benchmark); (b) cross-table consistency verification — a post-processing pass checking whether semantically equivalent source columns across tables receive identical target mappings; (c) human-in-the-loop interface evaluation implementing Matchmaker's entropy-based deferral (routing uncertain matches to human review) and Magentic-UI's co-planning pattern (expert reviews proposed column mappings before value mapping begins).

**The key empirical question is whether multi-agent orchestration adds value.** The evidence from Report C is cautionary: multi-agent systems fail 41-86.7% of the time across frameworks (Cemri et al., NeurIPS 2025), and sequential reasoning tasks degrade 39-70% under multi-agent coordination (Google DeepMind, Kim et al., 2026). However, N-table harmonization is genuinely parallelizable — each table's harmonization is independent — fitting the one scenario where multi-agent consistently helps. The hypothesis is that fan-out parallel processing with a lightweight merge/consistency check will outperform sequential processing (in wall time) while maintaining or improving accuracy (through cross-table consistency enforcement).

**Estimated effort.** 6-8 months for 1-2 researchers. Multi-agent implementation is the highest-risk component — if LangGraph orchestration proves brittle, the publication can focus on N-table results with sequential processing and RLM decomposition, positioning the multi-agent comparison as a negative result.

**Target venue.** SIGMOD 2028 (industry track, for the system design contribution), Journal of Biomedical Informatics (for the clinical application angle), or a second VLDB EA&B submission with the expanded benchmark.

### 3.3 P-Extra: Aspirational Future Work

These ideas are fully specified for immediate pickup when capacity allows. Each connects to the overall research narrative: Publication 1 asks "which approaches work?", Publication 2 asks "can we find AND harmonize?", Publication 3 asks "can we scale?", and P-Extra asks "can this change how labs actually work?"

**Production deployment study (Est. 6-12 months, requires collaboration).** Deploy the best-performing pipeline for a lab's actual research workflow — e.g., a cancer genomics group wanting to harmonize 50 GEO datasets for a meta-analysis. Measure time savings vs. manual curation (baseline: ~2-4 hours per dataset for experienced curators per Long et al. 2025), error rates on real queries (not benchmark tasks), user satisfaction via structured interviews, and the distribution of failure modes in production vs. benchmark settings. This is the ultimate validation: does the system actually save time and produce usable data? Requires collaboration with a wet-lab or clinical bioinformatics group.

**Cross-schema generalization (Est. 3-4 months).** Test whether models and pipelines trained/optimized for GDC generalize to other target schemas: ENCODE metadata standards, cBioPortal's data model, the Observational Medical Outcomes Partnership (OMOP) CDM (enabling direct comparison with Matchmaker's published MIMIC-OMOP results), and the Clinical Data Interchange Standards Consortium (CDISC) SDTM. If generalization holds, this transforms Gene Expression Omnibench from a GDC-specific tool to a universal harmonization benchmark.

**Fine-tuning domain-specific SLM (Est. 2-3 months).** Following Magneto's self-supervised approach, fine-tune a small language model (MPNet or BGE-base) specifically for GEO→GDC retrieval using LLM-generated synthetic training data. Magneto demonstrated that SLM fine-tuning improved GDC MRR from 0.551 to 0.860 — the same approach applied to GEO's free-text metadata could address the domain gap identified by "Toward Total Recall" (GEO recall 44% vs. BioSample 82%).

**Active learning from harmonization outcomes (Est. 3-4 months).** Build a feedback loop from harmonization success/failure back to search ranking. GSEs successfully harmonized into usable data become positive training signals; GSEs that score high in search but fail processing become hard negatives for retriever fine-tuning. Train a processability model on (GSE metadata → harmonization success) using historical outcomes and blend into ranking: `0.7 × relevance_score + 0.3 × processability_score`. OpenRAG and DRO demonstrate that joint retriever-downstream optimization yields 5-15% improvement over independent training.

**Community benchmark platform (Est. 2-3 months).** Build a public leaderboard on HuggingFace Spaces with automatic evaluation — researchers upload their system's predictions in a standardized format, and the platform computes all metrics, statistical comparisons, and cost-quality Pareto positions. Similar to MTEB but for metadata harmonization. This extends Gene Expression Omnibench's impact beyond the initial publications and creates a living benchmark that tracks progress as new models and methods emerge.

**Multi-modal harmonization (Est. 6-12 months, requires domain expansion).** Extend the benchmark and pipeline to cover proteomics (PRIDE repository, UniProt vocabulary), metabolomics (MetaboLights, ChEBI ontology), and clinical genomics (dbGaP, controlled-access). Each modality introduces different vocabulary conventions and metadata structures. The architecture (search → harmonize → evaluate) generalizes, but the gold standards and domain-specific context engineering do not.

---

## Gap Analysis and Open Questions

**The benchmark size vs. statistical power tradeoff.** The plan targets 200+ ground-truth column matches across 10+ tables, which provides adequate power (McNemar's test, power=0.80, α=0.05) to detect F1 differences of 0.10 between systems. However, to detect smaller differences (0.05) — which is the relevant granularity when comparing systems in the 70-80% accuracy range — would require 400-800 test instances. The fallback of ≥4 tables with ≥100 matches is borderline. This tension between annotation cost and statistical resolution is the single largest practical constraint on the benchmark's usefulness.

**The DSPy cold-start problem.** DSPy's BootstrapFewShot optimizer requires successful traces to bootstrap from, but the first runs on a new benchmark have no prior successes. Matchmaker addressed this by bootstrapping from the model's own successful zero-shot attempts, but this works only if zero-shot accuracy is sufficient to generate enough positive examples. If zero-shot performance on GEO metadata is poor (plausible given the 38-point GEO-BioSample gap), the bootstrapping loop may not converge. Fallback: use a small set of manually crafted demonstrations (5-10) as the initial seed. This is an open implementation question requiring empirical resolution in Month 2-3.

**Value mapping evaluation methodology.** Schema matching (column → column) has well-established metrics (F1, MRR, Recall@K). Value mapping (free-text → controlled vocabulary) lacks standardized evaluation. The proposed three-tier scoring (exact match, partial credit via Wu-Palmer similarity in NCIt, zero for unrelated) is reasonable but introduces subjectivity in the partial credit weight. The GDC's 200+ enumerated properties with case-sensitive permissible values provide ground truth for constrained fields, but free-text fields (e.g., treatment descriptions) have no single correct standardization. This is a fundamental measurement challenge the benchmark must address transparently.

**Reproducibility of frontier coding agent experiments.** Claude Code and Codex CLI are commercial products that may change behavior between API versions. The four-layer reproducibility strategy (LLM call caching, config snapshots, prompt versioning, materialized intermediates) helps, but cached results are specific to a model version that may be deprecated. Best practice: report the exact model version string, API access date, and `system_fingerprint` (OpenAI) for every run. Acknowledge that exact reproduction may not be possible and report variance across 3-5 runs as the measure of stability.

**The simplicity of the Dou 2020 benchmark.** The primary existing test case (Dou 2020: 17 columns, 190 rows) is at the simpler end of the complexity spectrum. It is plausible that all agent architectures perform well on it, producing a ceiling effect that obscures meaningful differences. The solution is to include both easy and hard tasks in the benchmark — some tables with clear lexical matches and some requiring deep domain knowledge (e.g., mapping free-text treatment descriptions to GDC's treatment ontology codes). The difficulty distribution should be deliberately skewed toward hard cases, since easy cases provide less discriminative information.

**Model roster volatility.** The model landscape changes faster than a 6-month research plan can track. Gemma 4 was released April 2, 2026 — one day before this plan was written. By Month 4, new models (Llama 4.1, Qwen 4, Claude 5) may be available. The architecture must support easy model addition via litellm's provider system. The paper should frame model-specific results as "representative of the frontier/local quality at time of evaluation" rather than definitive rankings.

**The search pipeline scope decision.** Whether the search pipeline (R1-R3) belongs in Publication 1 or 2 is a genuine strategic question. Including it makes the paper more comprehensive but risks diluting the schema matching contribution. Excluding it focuses the paper but leaves the "end-to-end" claim unsupported. The go/no-go at end of Month 3 resolves this: if search results are strong, include them; if the pipeline is incomplete or results are preliminary, defer to Publication 2 and frame Publication 1 as "harmonization-focused with search as future work."

**The Matchmaker reimplementation challenge.** No code is published. Algorithm 2 and Appendix C prompts provide sufficient architectural detail, but implementation choices (ColBERTv2 indexing parameters, candidate set sizes, MCQ prompt formatting) affect performance. The reimplementation may not exactly replicate published numbers. This is mitigated by (a) evaluating on the omics benchmark rather than claiming parity on MIMIC-OMOP, and (b) reporting the reimplementation as "Matchmaker-inspired compositional pipeline" rather than "Matchmaker." If performance is substantially lower than reported, investigate and document the discrepancy as a reproducibility finding.

---

## Further Reading

**Schema Matching and Harmonization**
- Seedat N, van der Schaar M. "Matchmaker: Self-Improving LLM Programs for Schema Matching." NeurIPS 2024 GenAI for Health Workshop. arXiv:2410.24105. *The current SOTA for zero-shot LLM-based schema matching; introduces compositional LM programs with DSPy bootstrapping.*
- Liu Y et al. "Magneto: Combining Small and Large Language Models for Schema Matching." PVLDB 18, 2025. arXiv:2412.08194. *SLM+LLM retrieval-reranking with the GDC-SM benchmark — the closest existing benchmark to Gene Expression Omnibench.*
- Gungor E et al. "SCHEMORA: Schema Matching via Multi-stage Recommendation and Metadata Enrichment." arXiv:2507.14376, July 2025. *Current highest hit rates on MIMIC-OMOP; first open-source LLM schema matcher.*
- Lopez R et al. "BDI-Kit: An AI-powered toolkit for biomedical data harmonization." Patterns (Cell Press), February 2026. *The toolkit this project extends; integrates Valentine, Magneto, and Harmonia.*
- Santos A et al. "Interactive Data Harmonization with LLM Agents." arXiv:2502.07132, 2025. *Harmonia's agent architecture for GDC harmonization; explicitly identifies benchmarking as open research.*
- Wang S et al. "LLMatch: A Unified Schema Matching Framework with LLMs." APWeb-WAIM 2025. arXiv:2507.10897. *Multi-table schema matching with Rollup/Drilldown; introduces SchemaNet benchmark.*
- Koutras C et al. "Valentine: Evaluating Matching Techniques for Dataset Discovery." IEEE ICDE, 2021. *The standard evaluation framework for schema matching; provides classical baselines.*
- Chen Z et al. "ConStruM: Constructive and Structural Schema Matching." January 2026. *Demonstrates that structured context engineering dramatically outperforms raw context for disambiguation.*

**Agent Architectures and Design**
- Wang X et al. "Executable Code Actions Elicit Better LLM Agents." ICML 2024. arXiv:2402.01030. *The foundational CodeAct paper; up to 20% higher success rates than structured tool calls.*
- Cemri M et al. "Why Do Multi-Agent LLM Systems Fail?" NeurIPS 2025 Datasets Track. arXiv:2503.13657. *The definitive failure analysis: 1,600+ traces, 14 failure modes, 41-87% failure rates.*
- Kim J et al. "Towards a Science of Scaling Agent Systems." Google DeepMind, January 2026. *180-configuration study showing multi-agent degrades sequential reasoning by 39-70%.*
- Kapoor S et al. "AI Agents That Matter." TMLR, 2024. arXiv:2407.01502. *Cost-accuracy Pareto evaluation methodology; demonstrates simple retry strategies can match complex agents.*
- Zhang E, Kraska T, Khattab O. "Recursive Language Models." MIT CSAIL, December 2025. arXiv:2512.24601. *Data as external environment; enables processing inputs 100× beyond context windows.*

**Omics Metadata and GEO Curation**
- Sundaram S, Gonçalves RS, Musen MA. "Toward Total Recall in Metadata Harmonization." GigaScience, 2025. *Critical finding: GEO recall (44%) trails BioSample (82%) by 38 points under identical LLM conditions.*
- Verbitsky A, Boutet P, Eslami M. "Metadata harmonization from biological datasets with language models." Bioinformatics Advances 5(1), 2025. *Fine-tuned GPT-2 achieves 96% in-dictionary but only 17% out-of-dictionary accuracy.*
- Long K et al. "Large-scale Manual Curation and Harmonization of Metadata." bioRxiv, November 2025. *212,027 samples across 468 studies; documents pervasive quality issues in real metadata.*
- Lim N et al. "Curation of over 10,000 transcriptomic studies to enable data reuse." Database, 2021. *The Gemma project: 10,811 GEO datasets with 10,215 ontology terms.*
- Adams T et al. "ADHTEB: A benchmark of text embedding models for semantic harmonization." J Prev Alzheimers Dis, January 2026. *Demonstrates MTEB rankings don't predict domain-specific harmonization performance.*

**Experimental Methodology**
- Khattab O et al. "DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines." ICLR 2024. *The optimization framework for compositional LM programs.*
- Demšar J. "Statistical Comparisons of Classifiers over Multiple Data Sets." JMLR 7, 2006. *The reference for non-parametric statistical tests across multiple benchmarks.*
- Weber LM et al. "Essential guidelines for computational method benchmarking." Genome Biology, 2019. *Standards for rigorous benchmark design in bioinformatics.*

**Observability and Reproducibility**
- OpenInference Specification. AI-specific OTel semantic conventions. arize-ai.github.io/openinference. *The standard for tracing LLM agent execution.*
- Hirn S et al. "A Reproducible Tutorial on Reproducibility in Database Systems Research." PVLDB 17, 2024. *VLDB's three-badge reproducibility system.*

**RAG and Search**
- Grigoriadis D et al. "Public Omics Explorer (POE)." Comp Struct Biotech J 27:4802-4812, 2025. *Semantic search over 250K+ GEO-linked records with SBioBERT + FAISS.*
- Al Nazi Z et al. "BMQExpander: Ontology-Guided Query Expansion for Biomedical Retrieval." arXiv:2508.11784, 2025. *Up to 22% NDCG improvement via UMLS/MeSH/NCI ontology expansion.*
- Santhanam K et al. "ColBERTv2: Effective and Efficient Retrieval via Lightweight Late Interaction." NAACL, 2022. *Per-token embeddings enabling fine-grained matching for reranking.*
