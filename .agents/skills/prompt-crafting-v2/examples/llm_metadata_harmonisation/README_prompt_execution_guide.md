# Deep Research Prompt Set: LLM-Based Omics Metadata Harmonization

## Overview

This directory contains **4 standalone deep research prompts + 1 synthesis prompt** designed to produce a comprehensive, literature-grounded research plan for the LLM-based omics metadata harmonization project (GEO-Harmonizer / Gene Expression Omnibench).

The prompts are modeled on the depth, specificity, and structure of the genomic sequence-to-function deep research prompts (5 pieces), adapted for the metadata harmonization domain.

---

## Execution Order

### Phase 1: Run Prompts A–D independently (in parallel)

Each prompt is **self-contained** and can be run as a separate Deep Research session. They can be run in parallel — they do not depend on each other's outputs.

| Prompt | Focus | Estimated DR time | Key outputs |
|--------|-------|-------------------|-------------|
| **A** | Schema matching & harmonization landscape | 30–45 min | SOTA review, benchmark design, failure taxonomy, comparison methodology |
| **B** | RAG & GEO search/discovery pipeline | 30–45 min | Retrieval architecture, evaluation framework, component comparison |
| **C** | Agent architectures (single vs. multi-agent) | 30–45 min | Architecture comparison, observability design, sandbox recommendations |
| **D** | Local LLMs, prompt optimization, methodology | 30–45 min | Model selection, quantization analysis, experimental design, statistics |

### Phase 2: Run Prompt E (Synthesis) with all outputs

After receiving the four reports from A–D, run Prompt E. **Paste the full outputs of Prompts A–D into the conversation** before or alongside Prompt E so the model can synthesize them.

| Prompt | Focus | Estimated DR time | Key outputs |
|--------|-------|-------------------|-------------|
| **E (Synthesis)** | 6-month plan + codebase architecture | 30–45 min | Prioritized experiment inventory, month-by-month timeline, go/no-go decisions, architecture diff, executive summary |

---

## What Each Prompt Covers

### Prompt A: Schema Matching & Harmonization Landscape
- Taxonomy of approaches (classical → embedding → LLM-based)
- Detailed review of Valentine, COMA, LLMatch, Magneto, Matchmaker (compositional LM program with DSPy self-improvement), BDI-Kit, ConstruM
- Omics domain gap analysis
- Benchmark task taxonomy (5 complexity levels)
- Gold standard construction methodology
- Comparison methodology (statistical tests, variables to test)
- Failure mode taxonomy for harmonization

### Prompt B: RAG & GEO Search/Discovery
- GEO-specific search challenges (structured+unstructured, multi-granularity, implicit relevance)
- Retrieval strategy comparison (BM25, dense, hybrid, ColBERT, agentic)
- Paper full-text integration cost-benefit
- Query understanding and refinement patterns
- Evaluation framework with semi-gold-standard GEO ID sets
- SOTA RAG ingredients (2025–2026 embedding models, rerankers, frameworks)
- Search-to-harmonization handoff design

### Prompt C: Agent Architectures
- Single-agent taxonomy (ReAct+tools, CodeAct, frontier coding agent, compositional LM program/Matchmaker-style, direct prompting)
- Multi-agent taxonomy (hierarchical, fan-out, recursive, critic/verifier)
- The simplicity vs. capability tradeoff (pi-coding-agent vs. SRAgent philosophies)
- Observability and tracing for scientific experiments
- Deterministic reproducibility requirements
- Human-in-the-loop interface patterns
- Sandboxed execution environments
- Specific architecture recommendations and implementation priorities

### Prompt D: Local LLMs, Optimization, Methodology
- Inference framework comparison (Ollama, vLLM, llama.cpp, SGLang)
- Model selection across 3 tiers (frontier, mid-range, small)
- Quantization impact on harmonization quality
- Prompt optimization approaches (DSPy, OPRO, manual, ConstruM-informed)
- Experimental design (sequential screening strategy, combinatorial explosion management)
- Statistical analysis methodology (paired tests, multiple testing, effect sizes)
- Cost-quality Pareto analysis
- Reporting standards for the benchmark paper
- Timeline feasibility assessment

### Prompt E (Synthesis): 6-Month Plan + Architecture
- Prioritized experiment inventory with Risk × Yield × Novelty scoring
- Month-by-month timeline with specific deliverables
- Go/no-go decision points
- Contingency plans
- Resource requirements
- Proposed codebase architecture (full directory tree)
- Diff from current research fork codebase
- Component interfaces and data contracts
- One-page executive summary

---

## Key Design Decisions

### Why 4+1 instead of one monolithic prompt?
1. **Context window limits**: A single prompt covering all aspects would exceed useful context even for deep research models
2. **Parallel execution**: 4 independent prompts can be run simultaneously, saving ~2 hours
3. **Quality**: Each focused prompt allows the model to do deeper research on its specific domain
4. **Iteration**: If one report is unsatisfactory, only that prompt needs to be re-run

### What the genomic deep research prompts taught us
- **Be extremely specific**: Name specific tools, papers, code repositories, and file paths
- **Include search instructions**: Tell the model exactly what web searches to run
- **Demand concrete outputs**: Experiment IDs, timeline with weeks, code examples, statistical tests
- **Include go/no-go decisions**: The plan must have decision points, not just a linear timeline
- **End with critical reminders**: Reinforce the most important constraints and priorities

### What's different from the genomic deep research prompts
- **Domain**: Computational genomics → data integration + NLP/LLM systems
- **Scope**: One pipeline → two pipelines (search + harmonization) + benchmarking
- **Architecture component**: The genomic deep research prompts didn't include a codebase architecture deliverable; this set does (in the synthesis prompt)
- **Baseline emphasis**: Strong emphasis on comparing against frontier coding agents as a baseline — this is the most provocative question in the project

---

## Appendix: Key URLs and Resources for the Deep Research Agent

Include these in your conversation for reference:

- Valentine benchmark: https://github.com/delftdata/valentine
- BDI-Kit: https://github.com/VIDA-NYU/bdi-kit
- LLMatch: search for "LLMatch Wang 2025 schema matching code"
- Magneto: search for "Magneto VLDB 2025 schema matching GDC"
- GDC Data Dictionary: https://docs.gdc.cancer.gov/Data_Dictionary/viewer/
- pi-coding-agent: https://mariozechner.at/posts/2025-11-30-pi-coding-agent/
- Claude Code repo: https://github.com/chatgptprojects/clear-code/
- DSPy: https://github.com/stanfordnlp/dspy
- MTEB Leaderboard: https://huggingface.co/spaces/mteb/leaderboard
- Phoenix (observability): https://github.com/Arize-ai/phoenix
