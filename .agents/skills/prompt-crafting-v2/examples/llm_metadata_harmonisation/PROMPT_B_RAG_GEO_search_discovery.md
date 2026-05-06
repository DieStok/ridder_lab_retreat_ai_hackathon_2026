# Deep Research Prompt B: RAG-Based Scientific Dataset Discovery Over GEO — Architecture, Evaluation, and SOTA Approaches

---

## PREAMBLE AND INSTRUCTIONS TO THE RESEARCH AGENT

You are a senior information retrieval researcher with deep expertise in: (1) retrieval-augmented generation (RAG) system design and evaluation, (2) scientific literature search and biomedical information retrieval, (3) embedding models and vector databases for domain-specific search, and (4) deep research agents and multi-step retrieval systems. You have been given context describing:

- **A GEO metadata database** with SQLite storage, FTS5 full-text search, and multi-stage extraction (Entrez API + SOFT files + web scraping) covering ~250,000+ GEO Series with title, summary, overall_design, organism, platform, sample characteristics, PubMed IDs, and supplementary file metadata.
- **Production RAG patterns** describing dual-pipeline architecture (offline indexing + online query), chunking strategies (semantic > fixed-size, 80% of RAG failures trace to chunking), embedding model selection, reranking, query transformation, and evaluation with RAGAS-type metrics.
- **BrowseComp-Plus** (Chen et al., 2025): A deep research agent benchmark evaluating multi-step information retrieval with complex queries. Relevant for evaluating open-ended scientific search agents.
- **Semi-gold-standard GEO ID sets**: The research group has classifiers for ALL prediction based on methylation profiles, providing near-complete lists of relevant GEO Series IDs for queries like "methylation data for ALL subtype classification." Similar semi-gold standards can be constructed for breast cancer survival expression data.
- **The pi-coding-agent philosophy** (Zechner, 2025): Minimal toolset, YOLO-by-default execution, context engineering as paramount, no sub-agents, cross-provider model support.

**Your task is to produce an exhaustive, technically rigorous research report** that addresses:

> ***How should a RAG-based search pipeline over GEO metadata (and optionally full-text papers) be designed, implemented, and evaluated to surface relevant studies for omics data harmonization queries — and what are the current best approaches for each component?***

---

## PART 1: RAG ARCHITECTURE FOR SCIENTIFIC DATASET DISCOVERY

### 1.1 The Specific Challenge of GEO Search

GEO search differs from standard document retrieval in several important ways. Analyze each:

1. **Structured + unstructured data**: GEO metadata combines structured fields (organism, platform, sample count, dates) with free-text (title, summary, overall_design). A query like "human breast cancer expression data with survival outcomes, >100 samples, from 2015 onwards" requires hybrid structured filtering + semantic matching.

2. **Multi-granularity**: Series-level metadata (GSE) vs. Sample-level metadata (GSM). A study might have an uninformative title but highly relevant sample characteristics. Should retrieval operate at GSE level, GSM level, or both?

3. **Implicit relevance**: A study on "gene expression in BRCA1 mutation carriers" may not mention "breast cancer survival" but is highly relevant. Semantic understanding of biomedical concepts is essential.

4. **Corpus size and update frequency**: ~250,000+ GEO Series (growing weekly). The RAG system must handle incremental updates efficiently.

5. **Long-tail queries**: Users may search for very specific data types ("Illumina 450K methylation arrays on pediatric acute lymphoblastic leukemia samples with treatment response data") where keyword matching fails.

For each challenge, describe: the state-of-the-art solution, what works in practice (with citations), and what remains unsolved.

### 1.2 Retrieval Strategy Comparison

Compare the following retrieval architectures for the GEO search task:

**Strategy 1: BM25/FTS5 baseline**
- SQLite FTS5 over title + summary + overall_design
- Advantages: Simple, fast, no embedding infrastructure
- Limitations: No semantic matching, keyword-dependent
- Expected performance: Good for precise queries, poor for conceptual queries
- **How to test**: Use the semi-gold-standard GEO ID sets; measure recall@K for K=10,50,100,500

**Strategy 2: Dense embedding retrieval**
- Embed GEO Series descriptions into a vector store
- Which embedding models? General-purpose (E5, BGE, GTE) vs. biomedical (PubMedBERT, BioSentVec, SapBERT)
- **Search for**: Which embedding models perform best for biomedical document retrieval as of 2025–2026? The MTEB leaderboard for biomedical domains.
- Vector database options: Qdrant, Milvus, ChromaDB, pgvector, FAISS. Which is best for ~250K documents with incremental updates?
- Chunking strategy: Should each GEO Series be a single chunk, or should title/summary/overall_design be separate chunks? What about sample-level characteristics?

**Strategy 3: Hybrid retrieval (BM25 + dense)**
- Reciprocal Rank Fusion (RRF) or linear combination of BM25 and dense scores
- **Search for**: Best practices for hybrid retrieval weighting as of 2025–2026. Reciprocal Rank Fusion vs. learned combination.
- Expected to outperform either alone based on production RAG literature

**Strategy 4: ColBERTv2 / late interaction models**
- Token-level interaction between query and document
- **Search for**: ColBERTv2 performance on biomedical retrieval. ColBERT-XM for multilingual. RAGatouille library for easy ColBERT deployment.
- Advantages: Better handling of complex multi-aspect queries. Can match on specific tokens.
- Limitations: Larger index size, slower than single-vector retrieval
- **Matchmaker evidence**: Matchmaker (Seedat & van der Schaar, 2024) uses ColBERTv2 multi-vector representations for its schema matching retrieval step, choosing it specifically for better expressivity and out-of-domain performance over single-vector approaches. Their use of RAGatouille for ColBERTv2 deployment provides a practical implementation reference.

**Strategy 5: Dual-source candidate generation (semantic + reasoning)**
- Combine retrieval-based candidates with LLM reasoning-based candidates, then refine
- **Matchmaker evidence**: This is the core innovation of the Matchmaker schema matching system. It generates semantic candidates via ColBERTv2 retrieval AND reasoning-based candidates via an LLM that reasons over the full target schema with CoT prompting. A refiner LLM then narrows the combined candidate set. Matchmaker demonstrates that reasoning-based candidates alone outperform semantic-only candidates (Table 3 in their paper), and the combination outperforms either alone on some tasks. This finding is directly transferable to GEO search: semantic retrieval may find studies with matching keywords, while LLM reasoning may identify studies that are conceptually relevant despite different terminology.
- For GEO search, this would mean: retrieve candidate GEO Series by embedding similarity, AND ask an LLM to reason about which studies might be relevant given the query and the GEO metadata schema, THEN combine and refine.

**Strategy 6: LLM-augmented retrieval (query expansion + reranking)**
- Use an LLM to expand the user query with biomedical synonyms and related concepts
- Use an LLM or cross-encoder to rerank top-K candidates
- **Search for**: LLM query expansion approaches for biomedical search. Cross-encoder reranking models (ms-marco, BGE-reranker).
- This adds latency and cost but can significantly improve recall for conceptual queries

**Strategy 7: Multi-step agentic retrieval**
- An LLM agent that iteratively refines its search: initial broad search → examine results → refine query → deeper search → critic evaluation
- **Search for**: Agentic RAG systems published 2025–2026. WebThinker (Li et al., 2025). STORM for knowledge synthesis. How do these relate to BrowseComp-Plus evaluation?
- Most complex but potentially highest recall for open-ended queries

For each strategy: estimate computational cost (indexing and query-time), expected recall@K, implementation complexity, and suitability for the GEO search task.

### 1.3 Incorporating Paper Full-Text

The research plan optionally includes downloading and indexing the full text of papers associated with each GEO Series (via PubMed IDs). Analyze:

1. **How much does paper text help?** Papers contain method details, cohort descriptions, and outcome data not present in GEO metadata. But they are much longer (5,000–50,000 tokens each). **Search for**: Studies comparing metadata-only vs. metadata+paper retrieval for scientific dataset discovery.

2. **Chunking strategies for papers**: Section-based chunking (Methods, Results, etc.), paragraph-level, or full-document summarization? The production RAG patterns document emphasizes that contextual headers improve retrieval; section titles are natural contextual headers for papers.

3. **Linking paper chunks to GEO Series**: Each paper chunk must be linked back to its GEO Series ID(s). This enables a two-stage retrieval: find relevant paper sections → retrieve associated GEO Series.

4. **Cost-benefit analysis**: For ~250K GEO Series, perhaps ~150K have associated papers. Downloading, parsing, chunking, and embedding ~150K papers is a significant infrastructure effort. Is the expected 10% improvement in retrieval (mentioned in the draft introduction) worth it?

5. **Supplementary materials**: These often contain the actual metadata tables. Can they be automatically extracted and used as additional context? **Search for**: Tools for automated supplementary material extraction from biomedical papers.

### 1.4 Query Understanding and Refinement

User queries for GEO data are often underspecified or use natural language that doesn't match GEO metadata terminology:

1. **Query decomposition**: "I want to build a classifier to predict all possible ALL subtypes based on methylation data" decomposes into: organism=human, disease=acute lymphoblastic leukemia, data_type=methylation, requirement=subtype annotations.

2. **Query expansion with domain knowledge**: Expanding "ALL" to "acute lymphoblastic leukemia" + "acute lymphocytic leukemia" + ICD codes. Expanding "methylation" to "DNA methylation" + "methylation array" + "Illumina 450K" + "Illumina EPIC" + "bisulfite sequencing."

3. **Iterative query refinement**: The agent retrieves initial results, examines them, and refines. For example: initial search returns 500 studies; agent samples 20, reads their metadata, and refines the query to exclude irrelevant study types (cell lines when the user wants patient samples).

4. **Critic subagents**: An orchestrator agent that spawns critic agents to evaluate candidate results. Each critic checks whether a GEO Series actually matches the query requirements. **Search for**: Critic/verifier patterns in LLM agent systems. How are these implemented in practice?

---

## PART 2: EVALUATION FRAMEWORK FOR GEO SEARCH

### 2.1 Metrics for Retrieval Quality

1. **Recall@K**: What fraction of relevant GEO Series are in the top K results? The primary metric when K is large (K=50–500) because users want comprehensive coverage for data harmonization.

2. **Precision@K**: What fraction of top K results are actually relevant? Important at K=10–20 for user-facing search.

3. **NDCG (Normalized Discounted Cumulative Gain)**: Accounts for ranking quality, not just set overlap.

4. **MAP (Mean Average Precision)**: Standard IR metric across queries.

5. **Latency**: End-to-end time from query to final result set. Important for interactive use.

6. **Cost**: Total token/API cost for multi-step agentic retrieval.

### 2.2 Gold Standard Construction for GEO Search

This is a major challenge. Analyze approaches:

1. **Semi-gold-standard from existing lab work**: The group has near-complete GEO ID lists for ALL methylation classification. These represent the best available ground truth. **How many such sets are needed for a meaningful evaluation?** Statistical considerations for evaluating search systems with small query sets.

2. **Expert-constructed query sets**: Have domain experts write 20–50 queries and manually identify relevant GEO Series for each. Time estimate: 2–4 hours per query if the expert must search GEO manually. For 30 queries = 60–120 person-hours.

3. **Programmatic semi-gold-standards**: Use structured GEO metadata to construct queries with known answers. Example: all GEO Series with organism="Homo sapiens" AND series_type contains "Methylation profiling" AND n_samples > 50 AND any PubMed ID → this gives a deterministic set. Then test whether the RAG system can recover this set from a natural language query.

4. **BrowseComp-Plus-inspired evaluation**: Construct queries that require multi-step reasoning to find the answer. Example: "Find GEO studies that measured expression in the same cohort as GSE12345 but used a different platform."

5. **Recall-only evaluation vs. precision-recall**: For the harmonization pipeline, false negatives (missing relevant studies) are more costly than false positives (including irrelevant studies, which will be filtered during harmonization). How does this asymmetry affect evaluation design?

### 2.3 Testing Each Component in Isolation

1. **Embedding model comparison**: Embed 1,000 GEO Series descriptions with 5–10 different embedding models. Use the gold-standard query sets to measure retrieval quality per model. **Search for**: How to efficiently compare embedding models for retrieval. MTEB-style evaluation protocols.

2. **Chunking comparison**: For the same embedding model, compare: (a) whole-document embedding, (b) field-level embedding (title separately, summary separately), (c) concatenated title+summary. **Search for**: "chunking strategy comparison RAG evaluation" — best practices.

3. **Reranker comparison**: Given a fixed retrieval set (top 100 from BM25), compare: (a) no reranking, (b) cross-encoder reranking (BGE-reranker, Cohere reranker), (c) LLM-based reranking (ask an LLM to score each result for relevance).

4. **Query expansion comparison**: (a) No expansion, (b) LLM synonym expansion, (c) ontology-based expansion using MeSH/DOID terms.

---

## PART 3: STATE-OF-THE-ART RAG INGREDIENTS (2025–2026)

### 3.1 What Has Changed Since 2024

**Search aggressively for the latest developments in each area:**

1. **Embedding models**: What are the current top models on MTEB? Have biomedical-specific models caught up with general models? **Search for**: "MTEB leaderboard 2026 biomedical embedding" and "best embedding model biomedical retrieval 2025 2026"

2. **Reranking**: Cross-encoder vs. LLM-based reranking cost-quality tradeoff. **Search for**: "reranking LLM vs cross-encoder 2025 2026"

3. **Agentic RAG**: The transition from passive RAG to active/agentic RAG where the LLM drives the retrieval process. **Search for**: "agentic RAG 2025 2026" and "self-RAG corrective RAG adaptive RAG"

4. **Evaluation frameworks**: RAGAS, DeepEval, Arize Phoenix for RAG evaluation. **Search for**: "RAG evaluation framework 2025 2026 best practices"

5. **Guardrails and hallucination detection in RAG**: How to ensure the search agent doesn't hallucinate GEO Series IDs. **Search for**: "RAG hallucination detection grounding 2025"

6. **Graph RAG and knowledge-graph-augmented retrieval**: Microsoft GraphRAG, LightRAG. Relevance for structured metadata like GEO? **Search for**: "GraphRAG structured metadata retrieval"

### 3.2 Infrastructure Choices

1. **Vector database**: Compare Qdrant, Milvus, ChromaDB, pgvector, Weaviate for the GEO use case (~250K documents, weekly incremental updates, metadata filtering, hybrid search support).

2. **Orchestration framework**: LangChain, LlamaIndex, Haystack, custom. Which is best for a scientific RAG pipeline that needs both deterministic filtering and LLM-based retrieval?

3. **Local vs. cloud**: The HPC environment uses Apptainer containers with SLURM. Can the RAG infrastructure run locally? GPU requirements for embedding + reranking? **Search for**: "self-hosted RAG pipeline GPU requirements"

---

## PART 4: CONNECTING SEARCH TO HARMONIZATION

### 4.1 The Handoff Problem

The search pipeline produces a set of GEO Series IDs. The harmonization pipeline ingests these IDs. What information should be passed between them?

1. **Minimal handoff**: Just the GSE IDs. The harmonization agent downloads metadata fresh.
2. **Rich handoff**: GSE IDs + retrieved metadata + relevance scores + paper sections that explain why each study was selected. This provides the harmonization agent with context about what to expect.
3. **Agent-mediated handoff**: The search agent writes a "data brief" for each GEO Series, summarizing what it found and what metadata challenges to expect. The harmonization agent reads this brief.

### 4.2 End-to-End Evaluation

How to evaluate the full pipeline (search → harmonization) as a single system:

1. **Cascaded evaluation**: Search recall × harmonization quality. If search finds 80% of relevant studies and harmonization succeeds on 75% of those, end-to-end success is 60%.
2. **Error attribution**: When the final output is wrong, was it a search failure (missed the study) or a harmonization failure (found the study but harmonized it incorrectly)?
3. **Joint optimization**: Does giving the harmonization agent more/less context from the search step affect its performance? Is there an interaction between search quality and harmonization quality?

---

## SEARCH QUERIES TO EXECUTE

1. "RAG biomedical scientific dataset discovery 2025 2026"
2. "GEO Gene Expression Omnibus search retrieval system"
3. "embedding model biomedical retrieval MTEB 2025 2026"
4. "ColBERTv2 biomedical document retrieval"
5. "agentic RAG multi-step retrieval scientific literature"
6. "BrowseComp deep research agent benchmark evaluation"
7. "hybrid retrieval BM25 dense biomedical"
8. "RAG evaluation RAGAS DeepEval 2025 2026"
9. "GraphRAG structured metadata knowledge graph"
10. "query expansion biomedical synonym ontology"
11. "self-hosted vector database comparison 2025 2026"
12. "chunking strategy scientific documents RAG"
13. "cross-encoder reranker biomedical"
14. "LlamaIndex Haystack scientific RAG pipeline"
15. "RAG hallucination detection grounding verification"

---

## CRITICAL REMINDERS

- **The GEO database is the specific corpus.** Not PubMed, not general web search. The retrieval system operates over structured GEO metadata (title, summary, overall_design, sample characteristics) and optionally associated paper full-text.
- **Recall is more important than precision** for this use case. Missing a relevant study is more costly than including an irrelevant one (which will be filtered during harmonization).
- **The system must handle incremental updates.** GEO grows weekly. The indexing pipeline must support efficient additions without full re-indexing.
- **Be concrete about infrastructure.** This runs on an HPC cluster with SLURM, Apptainer containers, and GPU nodes. Cloud-only solutions are not acceptable.
- **Connect search evaluation to the existing semi-gold-standard GEO ID sets.** These are the primary evaluation resource.
