# Deep Research Prompt A: LLM-Based Schema Matching and Metadata Harmonization for Omics Data — Landscape, Methods, and Benchmarks

---

## PREAMBLE AND INSTRUCTIONS TO THE RESEARCH AGENT

You are a senior data integration researcher with deep expertise in: (1) schema matching and mapping algorithms (classical, ML-based, and LLM-based), (2) biomedical metadata standards (GDC, OMOP CDM, Biolink), (3) large language model applications for data wrangling and entity resolution, and (4) omics data repositories (GEO, SRA, TCGA, ArrayExpress) and their metadata heterogeneity challenges. You have been given context describing:

- **BDI-Kit / Harmonia (published system)** (Lopez et al., Patterns 2026; Santos et al., 2025): An AI-powered toolkit for biomedical data harmonization using LLM agents with domain-specific tools (match_schema, rank_schema_matches, match_values, materialize_mapping, get_gdc_acceptable_values). The published system provides a human-in-the-loop LLM agent for metadata harmonization but lacks systematic benchmarking of model/harness combinations and does not address data discovery.
- **Our research codebase (forked from Harmonia)**: A heavily extended fork of the published Harmonia codebase, adapted for scientific experimentation. Key additions include: an Apptainer-sandboxed Beaker kernel environment, two primary agent paradigms (ReAct + BDI-Kit domain tools, and true CodeAct where the LLM writes Python directly), Phoenix/OTel tracing for observability, a 20-class failure taxonomy, automated experiment orchestration via YAML configs and SLURM, a Plotly Dash dashboard for experiment comparison, and support for both frontier (via litellm/OpenRouter) and local (Ollama) LLMs. This research fork is the testbed for the experiments described in this project and should be clearly distinguished from the published BDI-Kit/Harmonia system when reporting results.
- **LLMatch** (Wang et al., APWeb-WAIM 2025): A three-stage LLM-based schema matching framework with Rollup/Drilldown column consolidation, achieving F1 0.30–0.85 on multi-table tasks. Introduced the SchemaNet benchmark (7 datasets, finance/healthcare/entertainment).
- **ConstruM**: A study on selecting optimal context for LLM-based schema matching — directly relevant to the "what context should the LLM see?" variable.
- **The Alzheimer's embedding benchmark** (Adams et al., JPAD 2026): Domain-specific testing of text embedding models for semantic harmonization of Alzheimer's cohorts, showing that performance on general benchmarks does not predict domain-specific performance.
- **Magneto** (Liu et al., VLDB 2025): SLM retrieval + LLM reranking paradigm; GDC biomedical benchmark developed with NCI domain experts.
- **Valentine** (Koutras et al., ICDE 2021): The standard benchmark framework for schema matching in dataset discovery, implementing COMA, Cupid, Similarity Flooding, distribution-based matchers, and Jaccard-Levenshtein baselines.
- **A January 2026 comprehensive literature review** covering 20 years of schema matching evolution from classical approaches through LLM-based systems.

**Your task is to produce an exhaustive, technically rigorous research report** that addresses the central question:

> ***What is the current state of the art in LLM-based metadata harmonization, specifically for the omics/biomedical domain, and how should a benchmarking framework be designed to rigorously compare classical, embedding-based, and LLM-based approaches for both schema matching and value mapping on GEO metadata?***

---

## PART 1: TAXONOMY OF SCHEMA MATCHING AND VALUE MAPPING APPROACHES (2001–2026)

### 1.1 Classical and Composite Matchers

For each of the following systems, provide: (a) the core algorithm(s), (b) what types of matching they support (1:1, 1:n, n:1, n:m), (c) known strengths and failure modes, (d) availability and how to run them today, and (e) performance on standard benchmarks.

**Systems to cover (do not skip any):**

1. **COMA/COMA++** (Do & Rahm, 2002/2005) — 15+ individual matchers with configurable combination. The NamePath+Leaves configuration. How it performs on Valentine benchmarks.
2. **Cupid** (Madhavan et al., 2001) — Two-phase linguistic + structural matching. Known poor performance on complex tasks (F1 0.00–0.01 on MIMIC-OMOP per LLMatch).
3. **Similarity Flooding** (Melnik et al., 2002) — Graph-based propagation. Computational cost vs. benefit.
4. **Valentine framework implementations** — Distribution-based matchers, Jaccard-Levenshtein. The key finding that no single matcher dominates all scenarios.
5. **Unicorn** and other pre-transformer ML matchers — Search for what was SOTA before LLM approaches.

### 1.2 Embedding and Pre-trained Language Model Approaches

1. **DeepMatcher** (Mudgal et al., 2018) — RNN attention for entity matching. ER-Magellan benchmark.
2. **Ditto** (Li et al., 2020) — Fine-tuned BERT with 29% F1 improvement over DeepMatcher on entity matching.
3. **SapBERT / BioSentVec / PubMedBERT** — Domain-specific biomedical embeddings. Their use in biomedical entity linking and semantic matching.
4. **The Alzheimer's embedding study** (Adams et al., 2026) — Key finding: general-purpose embedding benchmarks don't predict domain-specific harmonization performance. Which embedding models performed best for clinical metadata? How does this translate to GEO omics metadata?
5. **Sentence-BERT / MPNet / E5 / BGE / GTE** — General-purpose embeddings used as the SLM retrieval component in hybrid systems. Which are best for metadata column matching? **Search for**: head-to-head embedding comparisons for schema matching as of 2025–2026.

### 1.3 LLM-Based Systems (2023–2026)

For each system, detail: architecture, prompting strategy, benchmark performance, cost analysis, and limitations.

1. **Magneto** (Liu et al., VLDB 2025) — The SLM retrieval + LLM reranking paradigm. Self-supervised SLM fine-tuning using LLM-generated synthetic data. Column serialization with 10 sample values per column (empirically optimal). The GDC biomedical benchmark. MRR improvements from 0.551 to 0.605. **Search for**: Has Magneto been applied to GEO/omics metadata specifically? Is the GDC benchmark publicly available?
2. **LLMatch** (Wang et al., July 2025) — Three-stage framework with Rollup/Drilldown. SchemaNet benchmark. Performance on MIMIC-to-OMOP (F1 0.30–0.85). The importance of hierarchical abstraction for context window management. **Search for**: LLMatch code availability. Can it be run with local models? What models were tested?
3. **Matchmaker** (Seedat & van der Schaar, NeurIPS GenAI for Health Workshop 2024, arXiv:2410.24105) — A self-improving compositional language model program for schema matching. This is a particularly important system to understand because it demonstrates several key architectural patterns relevant to our project:
   - **Architecture**: A 3-stage compositional LM program: (i) Multi-vector document creation using ColBERTv2 token-level embeddings for the target schema; (ii) Dual candidate generation combining semantic retrieval candidates (from the ColBERTv2 vector DB) AND reasoning-based candidates (LLM with CoT reasons over schema hierarchies) → a refiner LLM narrows these to a smaller candidate set; (iii) Confidence scoring using an MCQ format with an explicit "None of the above" abstain option, leveraging token-level LLM calibration for confidence scores (0–100).
   - **Self-improvement via DSPy bootstrapping**: Matchmaker uses synthetic in-context examples for zero-shot self-improvement. It runs its own pipeline on an unlabeled evaluation set, uses an LLM Evaluator to score the outputs, and selects the top-scoring input-output traces (including intermediate pipeline traces) as in-context demonstrations — adopting the DSPy bootstrapping process. This is **directly relevant** to our planned prompt optimization experiments.
   - **Key results**: acc@1 of 62.20% on MIMIC-OMOP and 70.20% on Synthea-OMOP, outperforming ReMatch (+20% at acc@1), Jellyfish (fine-tuned LLM), LLM-DP, and SMAT (supervised). The information retrieval formulation requires only ~1,340 LLM calls vs. ~24,771 for binary classification approaches — an O(n) vs. O(n²) scalability advantage.
   - **Critical sub-findings**: (a) Reasoning-based candidates outperform semantic-only candidates, suggesting LLM contextual reasoning over schema hierarchy is more valuable than embedding similarity alone; (b) Optimized in-context examples > random > vanilla > self-reflection, validating the DSPy bootstrapping approach; (c) GPT-3.5 Matchmaker matches GPT-4 ReMatch performance — the compositional multi-stage program compensates for a weaker backbone model, a critical finding for local model viability; (d) Entropy-based human deferral consistently outperforms random deferral, with errors often semantically close to true matches (amenable to post-hoc correction).
   - **Limitations for our project**: No code published as of the paper. Tested only on OMOP/MIMIC and Synthea-OMOP (clinical schemas, not omics). Operates on schema-level information only (no instance/value data). Supports m:1 matching but not n:m. **Search for**: Has Matchmaker code been released since the paper? Any follow-up work? Any application to omics/GEO metadata?
4. **ReMatch** (Sheetrit et al., 2024) — Uses retrieval to find semantically similar candidates, then a single LLM call to match. The closest prior work to Matchmaker but relies solely on semantic matching without reasoning-based candidates or self-improvement. Matchmaker outperforms it substantially. **Search for**: Has ReMatch been updated or extended since the original paper?
5. **Jellyfish** (Zhang et al., 2023) — An LLM fine-tuned specifically for data preprocessing tasks including schema matching. Despite being fine-tuned on the same MIMIC and Synthea datasets (giving it a training advantage), Jellyfish-13B achieves only 15.36% acc@1 on MIMIC vs. Matchmaker's 62.20% in zero-shot — a striking demonstration that compositional LM programs outperform fine-tuned models for this task. **Search for**: Jellyfish updates 2025–2026, any newer fine-tuned models for schema matching.
6. **BDI-Kit/Harmonia (published)** (Lopez et al., 2026; Santos et al., 2025) — Human-in-the-loop LLM agent with bdi-kit tools. The match_schema → rank_schema_matches → match_values → materialize_mapping pipeline. Important: the published system does not include systematic benchmarking of model/harness combinations. Our research fork extends this substantially (Apptainer sandboxing, automated experiments, tracing, multiple agent paradigms), but the *published* BDI-Kit/Harmonia is what should be cited and compared against in the literature review. **Search for**: Any published benchmarks for BDI-Kit. Are there studies comparing BDI-Kit performance across LLMs?
7. **Parciak et al. (2024)** — "Schema matching with large language models: an experimental study." Key finding that performance varies significantly with prompt design. **Search for**: Their specific findings on what prompt structures work best.
8. **Narayan et al. (2022)** — "Can foundation models wrangle your data?" Early work on foundation models for data integration. What did they find about capabilities and limitations?

**Search specifically for any systems published in late 2025 or 2026** that apply LLMs to schema matching, metadata harmonization, or data wrangling. The field moves very fast.

### 1.4 Value Mapping and Instance-Based Matching

Schema matching identifies which columns correspond; value mapping transforms actual values to conform to the target vocabulary. These are often assessed separately but must work together.

1. **Value standardization approaches**: Rule-based (regex, lookup tables), ML-based (entity linking), LLM-based (few-shot classification). Which approaches are used in each of the systems above?
2. **Controlled vocabulary mapping for biomedical data**: UMLS, SNOMED-CT, MeSH, NCI Thesaurus. How do current systems map free-text metadata values to controlled vocabularies? What role do ontology-aware approaches play?
3. **GDC-specific value mapping**: The GDC schema has specific acceptable values for each field (e.g., `primary_diagnosis` must be a valid ICD-O-3 code, `tissue_or_organ_of_origin` must match a specific vocabulary). How do current systems handle this constrained generation / value selection problem?
4. **The gap between schema matching and value mapping benchmarks**: Valentine tests schema matching only. LLMatch tests schema matching. Who benchmarks value mapping? **Search for**: Benchmarks that specifically evaluate value mapping / instance-level transformation quality for metadata harmonization.

### 1.5 The Omics Domain Gap

**This is the critical gap this project addresses.** Provide a thorough analysis:

1. **What benchmarks exist for omics/biomedical metadata harmonization?** The GDC benchmark in Magneto, the MIMIC-OMOP transformation, the Alzheimer's embedding study. **What is missing?** Specifically: benchmarks using GEO sample-level metadata tables, benchmarks testing harmonization to GDC schema with real GEO data, benchmarks testing multi-table harmonization (10 GEO studies → unified GDC-compliant table).

2. **What makes omics metadata harder than financial/entertainment data?** Context-dependence (the same column header "Stage" means different things in different cancer types), implicit metadata (biological sex implied by cancer type), domain-specific ontologies (ICD-O-3, UBERON, CL ontology), multi-modal metadata (clinical + molecular + sample processing), and variable quality (many GEO studies have minimal metadata).

3. **What existing work applies LLMs to GEO metadata specifically?** Search for:
   - "GEO metadata harmonization LLM" 
   - "Gene Expression Omnibus metadata standardization"
   - "omics metadata curation automated"
   - Verbitsky et al. (Bioinformatics Advances, 2025) — "Metadata harmonization from biological datasets with language models"
   - Long et al. (bioRxiv 2025) — "Large-scale Manual Curation and Harmonization of Metadata"
   - Piquer-Esteban et al. (BMC Bioinformatics, 2024) — "OMD Curation Toolkit"
   - Lim et al. (Database, 2021) — Curation of 10,000+ transcriptomic studies

4. **What biological ontologies are most relevant and how should they be made accessible to the LLM?** UBERON (anatomy), CL (cell types), DOID (diseases), NCIt (NCI Thesaurus), EFO (Experimental Factor Ontology), OBI (Ontology for Biomedical Investigations). Should these be embedded in a vector store for RAG? Provided as constrained generation vocabularies? Fine-tuned into the model?

---

## PART 2: BENCHMARK DESIGN FOR OMICS METADATA HARMONIZATION

### 2.1 Task Taxonomy

Define a clear taxonomy of benchmark tasks, ordered by complexity:

**Task Level 1: Single-table schema matching to a reference schema (e.g., GDC)**
- Input: One GEO metadata table (e.g., Dou 2020 endometrial carcinoma, 17 columns, 190 rows)
- Target: GDC schema column names
- Output: Column-to-column mapping
- Evaluation: Precision, recall, F1 on column mapping correctness

**Task Level 2: Single-table schema + value mapping**
- Same as Level 1, plus: for each mapped column, transform all values to GDC-acceptable values
- Evaluation: Column mapping metrics + per-column value accuracy/F1 (including handling of missing values, hallucinations, omissions)

**Task Level 3: Two-table harmonization**
- Input: Two GEO metadata tables from different studies
- Target: Harmonized table with unified schema
- Subtask: Map each table to GDC independently, then merge
- Evaluation: Both table-to-schema mapping quality AND row-level merge correctness

**Task Level 4: N-table harmonization (N=5–10)**
- Input: N tables from related studies (e.g., all CPTAC cancer studies)
- Target: Single unified GDC-compliant table
- Evaluation: Schema mapping per table, value mapping per table, cross-table consistency, final merged table quality

**Task Level 5: End-to-end (search + harmonization)**
- Input: Natural language query (e.g., "breast cancer survival expression data")
- Target: Discover relevant GEO studies AND harmonize their metadata
- Evaluation: Search recall + harmonization quality

For each task level, specify: what metrics to use, what constitutes a gold standard, how to handle partial correctness, and what the minimum benchmark set size should be for statistical significance.

### 2.2 Gold Standard Construction

**This is perhaps the most valuable contribution.** Detail how to construct gold standards:

1. **For schema matching**: Human expert annotation of column mappings from GEO tables to GDC schema. How many annotators? What inter-annotator agreement protocol (Cohen's κ, Fleiss' κ)? How to handle ambiguous cases where multiple valid mappings exist?

2. **For value mapping**: Human expert annotation of correct transformed values. How to handle cases where the source value has no exact GDC equivalent? How to score "close but not exact" mappings?

3. **For multi-table harmonization**: The Li 2023 ground truth for 10 CPTAC studies already exists. What other multi-table gold standards can be constructed? **Search for**: Existing curated GEO metadata collections that could serve as gold standards.

4. **How many test cases are needed?** Statistical power analysis for comparing two systems on schema matching with expected F1 difference of 0.05–0.10. How many tables × columns × values are needed?

### 2.3 Comparison Methodology

How to fairly compare the systems from Part 1 against each other on omics data:

1. **Valentine baselines**: Run all Valentine matchers (COMA, Cupid, Similarity Flooding, distribution-based, Jaccard-Levenshtein) on the omics benchmark tasks. Use `pip install valentine` and the standard API.

2. **Embedding baselines**: Run the top embedding models from the Alzheimer's study on the same tasks. Include at least: MPNet, E5-large-v2, BGE, PubMedBERT, SapBERT.

3. **LLM-based systems**: Run LLMatch, Magneto (if code available), and the published BDI-Kit system on the omics benchmark tasks. Reimplement the Matchmaker compositional LM program (candidate generation → refinement → MCQ confidence scoring with abstain) since no code is published — the paper provides sufficient algorithmic detail (Algorithm 2 in their appendix) and prompt examples (Appendix C) for reimplementation. Additionally, test the two primary agent paradigms in our research fork (ReAct + BDI-Kit domain tools, and CodeAct). Include frontier models (Claude Sonnet 4.6, GPT-5-mini, Gemini 2.5 Flash) AND local models (Qwen 3.5 27B, Mistral Nemo, Devstral, Llama variants). When reporting results, clearly distinguish between the published BDI-Kit system's performance and our research fork's performance under different configurations.
   - **Important architectural comparison**: Matchmaker's compositional LM program (multi-stage, no agent loop, no tool use) vs. BDI-Kit's agent-with-tools vs. CodeAct's coding agent represent fundamentally different paradigms for the same task. The finding that Matchmaker's GPT-3.5 variant matches ReMatch's GPT-4 performance (Table 6 in their paper) suggests that a well-designed multi-stage pipeline may be more important than raw model capability — directly relevant to our local model experiments.
   - **Candidate generation strategy**: Matchmaker demonstrates that combining semantic retrieval candidates with LLM reasoning-based candidates outperforms either alone (Table 3). This dual-source pattern should be tested in our pipeline: does giving the harmonization agent both embedding-based candidate matches AND LLM-reasoned candidates improve over either source alone?

4. **Frontier coding agents as baselines**: Run Claude Code and ChatGPT Codex in full-auto mode on the same tasks (given a CLAUDE.md/skills file with GDC schema context). This tests: "does a bespoke pipeline outperform just giving a frontier coding agent the data and letting it figure it out?"

5. **Statistical comparison**: Paired tests (McNemar's test for binary outcomes, Wilcoxon signed-rank for continuous metrics) with Bonferroni correction. Effect sizes (Cohen's d). Confidence intervals. Note that Matchmaker reports results over 5 seeds with standard deviations — we should follow at least this standard.

### 2.4 Variables to Test

Enumerate ALL variables that could affect performance, and propose which to test first:

1. **LLM choice**: Frontier (Claude, GPT, Gemini) vs. mid-tier (Qwen, Mistral) vs. small local (<10B parameters). Note Matchmaker's finding that GPT-3.5 with a compositional pipeline ≈ GPT-4 with a simple pipeline — model choice may interact strongly with architecture choice.
2. **Agent harness / pipeline formulation**: ReAct + domain tools vs. CodeAct vs. minimal coding agent vs. compositional LM program (Matchmaker-style, no agent loop) vs. no agent (direct prompting). Matchmaker demonstrates that the IR formulation (candidate generation → refinement → ranking) dramatically outperforms binary classification on the Cartesian product, reducing LLM calls from O(n²) to O(n). This formulation choice is itself a key variable.
3. **Candidate generation strategy**: Semantic retrieval only vs. LLM reasoning only vs. dual-source (per Matchmaker's finding that dual outperforms single-source). For our task, this translates to: should the agent first retrieve candidate GDC columns by embedding similarity, then reason over them? Or reason from scratch? Or both?
4. **Context content**: What information is in the system prompt and tool descriptions? (per ConstruM findings)
5. **Number of example values per column**: 0, 5, 10, 20, all (per Magneto's finding that 10 is optimal). Note: Matchmaker operates without instance data, relying solely on schema-level information — testing whether adding instance data improves over schema-only matching is itself a variable.
6. **Schema representation**: Full GDC schema vs. pruned relevant subset vs. few-shot examples
7. **Ontology access**: None vs. embedded in prompt vs. RAG-retrieved vs. tool-accessible
8. **Temperature and reasoning settings**: Temperature 0.0 vs. 0.2; extended thinking on/off
9. **Multi-turn vs. single-turn**: Does iterative refinement with human feedback improve results? Matchmaker's entropy-based deferral provides a principled way to select which items to escalate to humans.
10. **Context window management**: Summarization, sliding window, recursive decomposition (per the recursive language models paper)
11. **Prompt optimization**: Manual prompts vs. DSPy-optimized prompts (with proper train/test splits). Matchmaker demonstrates that DSPy-style bootstrapping with synthetic in-context examples yields +5% acc@1 improvement over vanilla, and that systematic selection outperforms random selection — a direct validation of this optimization approach for schema matching.

**Which of these variables have the highest expected impact?** Propose a priority ordering based on the literature. Which can be tested in parallel? Which require sequential testing due to dependencies?

---

## PART 3: FAILURE MODE TAXONOMY

### 3.1 Known Failure Modes from the Literature and from Our Research Fork's Existing Taxonomy

Our research fork of Harmonia has a 20-class failure taxonomy (v1.2) across 6 categories, developed through extensive experimentation with multiple LLMs on the GDC harmonization task. This taxonomy is not part of the published BDI-Kit/Harmonia system. Extend this with failures specific to metadata harmonization:

1. **Schema matching failures**: Wrong column mapping, missing mapping, hallucinated target column, many-to-one collapse (mapping multiple source columns to the same target), compositional mapping failure (failing to split "full_name" into "first_name" + "last_name")
2. **Value mapping failures**: Incorrect value transformation, hallucinated values not in GDC vocabulary, omitted values, format errors (e.g., date format wrong), ontology code errors (wrong ICD-O-3 code)
3. **Context-dependent failures**: Misinterpreting domain-specific column meanings, failing to use implicit knowledge (e.g., prostate cancer → male patients), incorrectly applying one study's conventions to another
4. **Multi-table failures**: Inconsistent mappings across tables, merge conflicts, duplicate row handling errors
5. **Agent-level failures**: Tool use errors, infinite loops, context window exhaustion, premature termination
6. **Infrastructure failures**: Model unavailability, token limit exceeded, API rate limiting

For each failure mode: provide an example, estimate how common it is (based on literature or our research fork's experience), and propose detection/mitigation strategies.

### 3.2 What Practitioners Need to Know

Based on the failure taxonomy, what are the top 10 practical recommendations for someone deploying an LLM-based metadata harmonization system? Structure these as actionable guidelines.

---

## SEARCH QUERIES TO EXECUTE

1. "LLM schema matching biomedical metadata 2025 2026" — latest systems
2. "GEO metadata harmonization automated" — GEO-specific work
3. "Valentine benchmark schema matching LLM" — LLM integration with Valentine
4. "Magneto schema matching GDC benchmark code" — Magneto availability
5. "LLMatch schema matching code repository" — LLMatch availability
6. "Matchmaker Seedat schema matching compositional language model program" — Matchmaker code release, follow-up work, applications beyond MIMIC/Synthea
7. "Jellyfish LLM data integration schema matching 2025" — Jellyfish updates
8. "compositional LLM program schema matching candidate generation refinement" — systems similar to Matchmaker's multi-stage approach
9. "value mapping benchmark metadata standardization" — value mapping benchmarks
9. "GDC schema harmonization tools automated" — GDC-specific tools
10. "omics metadata curation LLM agent" — omics-specific approaches
11. "DSPy prompt optimization schema matching" — prompt optimization for this task
12. "ConstruM context selection schema matching" — ConstruM details
13. "BDI-Kit benchmark comparison LLM models" — BDI-Kit evaluations
14. "coding agent vs domain tools data integration" — CodeAct vs. tool-based comparison
15. "inter-annotator agreement schema matching gold standard" — gold standard construction methods

---

## CRITICAL REMINDERS

- **Focus on the omics/GEO domain.** Financial and entertainment data benchmarks are context, not the target. The central question is: how do these approaches perform on GEO metadata specifically?
- **Be concrete about what code and data is available.** For each tool/system, state whether the code is open-source, where to get it, and whether it can be run with local models.
- **Always connect back to the GDC schema.** This is the primary target schema for harmonization. The GDC data dictionary is publicly available at https://docs.gdc.cancer.gov/Data_Dictionary/viewer/.
- **Distinguish schema matching from value mapping.** These are related but different tasks requiring different evaluation.
- **Search aggressively for 2025–2026 papers.** This field is evolving very fast.
