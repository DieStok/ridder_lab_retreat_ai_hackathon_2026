# Deep Research Prompt: Leveraging Sequence-Based Expression Prediction Models (PARM, Borzoi/Flashzoi, AlphaGenome) to Interrogate, Prioritize, and Validate Disease-Associated Non-Coding SNPs

---

## PREAMBLE AND INSTRUCTIONS TO THE RESEARCH AGENT

You are a senior computational genomics researcher with deep expertise in: (1) sequence-based deep learning models for gene regulation (Enformer, Borzoi/Flashzoi, PARM, AlphaGenome, DeepSEA, Sei), (2) human genetics and GWAS/PRS methodology, (3) cancer genomics and non-coding variant interpretation, and (4) population genetics including linkage disequilibrium, haplotype structure, and purifying selection. You have been given an extensive set of source materials describing:

- **The PARM model** (Barbadilla-Martínez et al., Nature 2026): a cell-type-specific CNN trained on MPRA data from human promoters, capable of predicting autonomous promoter activity from DNA sequence alone with Pearson's R = 0.84–0.93 across 10 cell types. PARM has 742,337 parameters, takes 600 bp input fragments, and can score ~435 variants per second on a GPU. It identifies regulatory sites (RSs) via in silico saturated mutagenesis (ISM) and has been shown to correctly predict TERT promoter cancer mutations and cis-eQTL effects.
- **A PARM-based cancer somatic eQTL study** (van Lieshout et al., medRxiv 2025): demonstrating that PARM can be used to identify promoter regions enriched for functional non-coding somatic mutations across 24,529 whole-tumour genomes. This study identified 492 promoter regions enriched for putatively functional SNVs, confirmed somatic eQTLs for 9 genes (including TERT, TP53, PMS2), and showed that functional promoter mutations are enriched in established cancer-driver genes.
- **AlphaGenome** (Avsec et al., Nature 2026): a unified DNA sequence model taking 1 Mb input and predicting thousands of functional genomic tracks at base-pair resolution, achieving SOTA on 25/26 variant effect prediction benchmarks, with eQTL sign auROC of 0.80 and coefficient Spearman ρ of 0.49.
- **Cancer Genetic Risk Panels & PRS Reference**: detailed panels of known risk genes, PRS models, and GWAS loci for breast cancer (PRS313, >300 SNPs across 170+ loci), liver cancer/HCC (PNPLA3, TM6SF2, PRS-5, PRS-combined with 15 loci), and prostate cancer (GRS451 with 451 variants, PRS130 from BARCODE1 trial).

**Your task is to produce an exhaustive, technically rigorous research report followed by a concrete, prioritized five-month research plan** that addresses the central research question:

> ***Can cell-type-specific, sequence-based deep learning models that have learned the regulatory grammar of the genome (PARM, Borzoi/Flashzoi, AlphaGenome) be used to make biologically meaningful predictions about known disease-associated non-coding SNPs — and can these predictions reveal new biology about haplotype-level combinatorial variant effects, purifying selection on regulatory variants, and the gap between theoretically worst-case and observed haplotypes in human populations?***

This decomposes into the following sub-questions:

1. **Validation**: Do these models predict larger expression effects for established PRS-included SNPs than for SNPs that were initially GWAS-associated but excluded from final PRS models (e.g., due to being population artefacts)?
2. **Combinatorial prediction**: Can iterative in silico mutagenesis with PARM (local, fast) combined with longer-range scoring via Borzoi/Flashzoi or AlphaGenome predict combinatorial haplotype-level expression effects that go beyond single-SNP additivity?
3. **Population validation**: Do the predicted extreme haplotypes (combinations of expression-altering variants) correspond to observed disease risk in real population data (UK Biobank, gnomAD, 1000 Genomes)?
4. **Selection signal**: Is there evidence of purifying/negative selection against the most extreme predicted haplotypes — i.e., are the theoretically worst-case combinations of regulatory variants underrepresented in healthy populations relative to expectation?
5. **Model benchmarking**: How do PARM (lightweight, promoter-focused, MPRA-trained), Borzoi/Flashzoi (large, RNA-seq-trained, long-range), and AlphaGenome (1 Mb context, multimodal) compare and complement each other for this specific task?

**Output requirements:**

- **Part 1**: Comprehensive review of all relevant sequence-based models, their architectures, training data, strengths, limitations, and computational costs
- **Part 2**: Landscape analysis of existing approaches for using sequence-based models to interpret disease-associated variants, including the latest papers and benchmarks
- **Part 3**: Detailed analysis of the proposed experimental framework — every step, every alternative, every data source
- **Part 4**: Specific testable hypotheses with experimental protocols, expected outcomes, and critical gaps in the current approach
- **Part 5**: Synthesis Agent output — a prioritized five-month plan with risk × yield scoring, go/no-go criteria, and a one-page executive summary

---

## PART 1: COMPREHENSIVE REVIEW OF SEQUENCE-BASED PREDICTION MODELS FOR REGULATORY VARIANT INTERPRETATION

### 1.1 Taxonomy of Models: Architecture, Training Data, and Capabilities

For each of the following models, provide: (a) the core architecture and input/output specifications, (b) what training data was used and how this shapes what the model can and cannot predict, (c) computational cost for inference (variants per second, GPU requirements), (d) known strengths and failure modes with citations, (e) which cell types/tissues are covered, and (f) availability of code/weights/API.

**Models to cover in depth (do not skip any):**

1. **PARM (Promoter Activity Regulatory Model)** — Barbadilla-Martínez et al., Nature 2026
   - Architecture: CNN with self-attention pooling layers, 742,337 parameters. Input: 600 bp one-hot encoded DNA. Output: predicted promoter activity (scalar).
   - Training data: MPRA data from ~10 million random genomic fragments overlapping 30,607 curated human promoters. Separate models per cell type (K562, HepG2, MCF7, LNCaP, HCT116, U2OS, HEK293, AGS, HAP1, plus CRC organoid).
   - Key capability: predicts *autonomous* promoter activity — i.e., the intrinsic regulatory potential of a sequence without distal enhancers, chromatin context, or epigenetic modifications. This is a reductionist model.
   - Variant scoring: in silico saturated mutagenesis (ISM) — predict activity for reference sequence, predict for all 3 alternative nucleotides at each position, compute importance score.
   - Speed: ~435 variants/second on NVIDIA A40 GPU. Training: ~1 day on 12 cores, 10 GB RAM, one RTX6000 GPU per cell type.
   - Limitations: (i) Only models promoter-proximal effects (up to ~300 bp upstream, ~100 bp downstream of TSS). (ii) No distal enhancer effects. (iii) No chromatin context. (iv) Cell-type models limited to cell lines with available MPRA data.
   - **Search for**: Has PARM been applied to germline disease variants beyond the van Lieshout et al. somatic cancer study? Are there other PARM applications published in 2025–2026?

2. **Enformer** — Avsec et al., Nature Methods 2021
   - Architecture: Transformer-based, ~250M parameters. Input: 393,216 bp. Output: 896 bins × 5,313 tracks (128 bp resolution). Predicts CAGE, DNase, histone ChIP-seq tracks.
   - Limitation: 128 bp resolution blurs fine-scale effects. eQTL prediction performance: sign auROC ~0.75, coefficient Spearman ρ ~0.35 (prior to AlphaGenome).
   - **Search for**: Enformer's specific performance on cancer risk loci. Any published studies using Enformer for PRS variant scoring.

3. **Borzoi** — Linder et al., Nature Genetics 2025
   - Architecture: convolutional + transformer, >30 million parameters. Input: 524,288 bp. Output: RNA-seq coverage predictions at 32 bp resolution. Predicts RNA-seq coverage directly (not just CAGE), enabling more direct gene expression predictions.
   - Key advance over Enformer: predicts RNA-seq coverage as a unifying modality, better long-range predictions.
   - **Flashzoi**: Search for whether "Flashzoi" is a published distilled/fast version of Borzoi, or a community tool. Clarify its relationship to Borzoi. If not published, note this and recommend using Borzoi directly.
   - Speed: ~0.71 variants/second — approximately 600× slower than PARM. This has major implications for the proposed combinatorial mutagenesis approach.
   - **Search for**: All papers using Borzoi for disease variant interpretation published 2025–2026. Borzoi's performance on cancer GWAS loci specifically.

4. **AlphaGenome** — Avsec et al., Nature 2026
   - Architecture: U-Net-like with Encoder (conv blocks + max pooling, 1 bp → 128 bp), Transformer Tower (128 bp resolution), Decoder (upsampling back to 1 bp). Input: 1 Mb. Output: thousands of tracks including RNA-seq, CAGE, PRO-cap, splice sites, DNase-seq, ATAC-seq, histone ChIP-seq, Hi-C/Micro-C — all at up to base-pair resolution.
   - SOTA on 25/26 variant effect prediction benchmarks. eQTL coefficient Spearman ρ = 0.49 (vs. 0.39 Borzoi), sign auROC = 0.80 (vs. 0.75 Borzoi).
   - Available via API (non-commercial). Inference: <1 second per variant on H100.
   - Key advantage for this project: multimodal predictions allow assessing whether a variant affects expression via chromatin, TF binding, splicing, or other mechanisms.
   - **Search for**: AlphaGenome applications to cancer risk loci. Any studies using AlphaGenome for PRS validation or haplotype-level analysis.

5. **Sei** — Chen et al., Nature Genetics 2022
   - Sequence-based model predicting 21,907 chromatin profiles from 4,096 bp input. Provides a "sequence class" framework grouping variants into regulatory categories.
   - **Search for**: How Sei has been applied to disease variant interpretation. Compare with PARM/Borzoi.

6. **DeepSEA / ExPecto** — Zhou & Troyanskaya, Nature Methods 2015 / Zhou et al., Nature Genetics 2018
   - Earlier-generation models. ExPecto specifically predicts tissue-specific gene expression from sequence. Important as a comparison baseline.
   - **Search for**: How ExPecto's variant effect predictions compare with PARM/Borzoi/AlphaGenome on benchmarks.

7. **ChromBPNet** — Pampari et al., 2023
   - Specialized for chromatin accessibility at base-pair resolution from short sequences. Relevant because chromatin accessibility changes are a proximal mechanism by which regulatory variants affect expression.
   - **Search for**: ChromBPNet applications to disease variant interpretation.

8. **DeepSTARR** — de Almeida et al., Nature Genetics 2022
   - MPRA-trained model for enhancer activity prediction (Drosophila and human). Similar philosophy to PARM but focused on enhancers.
   - Relevant as a comparison for MPRA-trained models vs. epigenome-trained models.

### 1.2 Critical Comparison: MPRA-Trained vs. Epigenome-Trained Models

Provide a dedicated analysis of the fundamental difference between models trained on:
- **MPRA/reporter data** (PARM, DeepSTARR): These learn *causal* sequence-to-activity relationships because the assay directly measures whether a sequence autonomously drives transcription. However, they miss chromatin context, distal effects, and three-dimensional genome organization.
- **Epigenome/transcriptome data** (Enformer, Borzoi, AlphaGenome): These learn *correlative* relationships between sequence and epigenomic/expression state. They capture long-range effects and chromatin context but can be confounded by autocorrelative patterns, linkage disequilibrium in the training data, and cannot distinguish causal from correlative regulatory elements.

**For this project specifically**: How does this difference affect the interpretation of variant effect predictions? If PARM predicts a large effect and Borzoi/AlphaGenome do not (or vice versa), what does each discordance scenario mean biologically?

**Search for**: Papers that directly compare MPRA-trained and epigenome-trained model predictions for the same variants. The PARM paper (Barbadilla-Martínez et al.) compares PARM vs. Enformer vs. Borzoi on ISM and eQTL prediction — describe these results in detail. Also search for Karollus et al. (Genome Biology 2023) on promoter vs. distal enhancer prediction accuracy.

### 1.3 Computational Cost Analysis for the Proposed Framework

The proposed project involves:
- **Step 1**: ISM with PARM across all PRS loci (~1,000 SNPs × ~1,400 bp promoter windows = ~4.2 million single mutations). At 435 variants/second, this is approximately **2.7 hours** of GPU time. Feasible.
- **Step 2**: Combinatorial mutagenesis (pairs of mutations within each bin). If top 10 per bin and 20 bins per locus, that's C(200, 2) = ~19,900 pairs × 1,000 loci = ~20 million combinations. At 435 var/sec, this is **~12.7 hours**. Feasible.
- **Step 3**: Scoring selected haplotypes with Borzoi. If 1,000 candidate haplotypes per locus × 100 loci = 100,000 scores. At 0.71 var/sec, this is **~39 hours**. Feasible but slow.
- **Step 4**: Scoring with AlphaGenome via API. At <1 sec/variant but with API rate limits, need to estimate. **Search for** AlphaGenome API rate limits and batch capabilities.

Provide a detailed computational budget for each step, including realistic estimates of GPU costs (cloud pricing for A100/H100), expected wall-clock time, and bottlenecks.

### 1.4 Model Availability and Practical Considerations

For each model, confirm:
- Is the code publicly available? Where?
- Are pre-trained weights available for the relevant cell types (especially: breast cancer → MCF7; liver cancer → HepG2; prostate cancer → LNCaP)?
- Can the model be run locally, or only via API?
- Are there known bugs, versioning issues, or reproducibility concerns?

**PARM**: Code at https://github.com/vansteensellab/PARM. Models available for K562, HepG2, MCF7, LNCaP, HCT116, U2OS, HEK293, AGS, HAP1, CRC organoid. Interactive browser at http://parm.deridderlab.nl.

**Borzoi**: Search for the current repository and model availability. Note that the PARM paper (van Lieshout et al.) reports using Borzoi by averaging over all GTEx RNA tracks.

**AlphaGenome**: API at http://deepmind.google.com/science/alphagenome. Python SDK available. Code/weights at https://github.com/google-deepmind/alphagenome_research.

**Search for**: Any practical guides or tutorials for running these models on disease variants. Community tools or pipelines that wrap multiple models.
## PART 2: LANDSCAPE ANALYSIS — EXISTING APPROACHES FOR INTERPRETING DISEASE-ASSOCIATED VARIANTS WITH SEQUENCE-BASED MODELS

### 2.1 Timeline of Key Developments (2019–2026)

Construct a detailed chronological timeline of the ~30 most important papers and tools at the intersection of sequence-based deep learning models and disease variant interpretation. For each entry, provide: the key insight, why it mattered, and what it enabled downstream. **Search the web for any major papers from 2025–2026 that may not be in the provided materials.**

Structure the timeline around these thematic arcs:

1. **The Foundation Models Era (2019–2022)**:
   - DeepSEA/ExPecto (Zhou et al., 2015/2018) → Basenji/Basenji2 (Kelley et al., 2018/2020) → Enformer (Avsec et al., 2021) → Sei (Chen et al., 2022)
   - The key transition: from predicting binary chromatin states to predicting continuous-valued expression/accessibility tracks
   - How each model improved variant effect prediction benchmarks

2. **The MPRA + Deep Learning Convergence (2022–2026)**:
   - DeepSTARR (de Almeida et al., 2022) → PARM (Barbadilla-Martínez et al., 2026) → Agarwal et al. (Nature 2025) massively parallel characterization
   - The insight: MPRA data provides *causal* training signal. Models trained on MPRA data may have higher precision for identifying causal variants even if they miss long-range effects.
   - Duttke et al. (Nature 2024) — position-dependent function of human TFs. How this relates to PARM's findings on TF positional grammar.

3. **Long-Range Models and RNA-seq Prediction (2024–2026)**:
   - Borzoi (Linder et al., 2025) → AlphaGenome (Avsec et al., 2026)
   - The shift from CAGE-based to RNA-seq-based expression prediction
   - Dudnyk et al. (Science 2024) — sequence basis of transcription initiation
   - Fu et al. (Nature 2025) — foundation model of transcription across cell types

4. **Application to Disease Genetics (2022–2026)**:
   - Fine-mapping with sequence models: How sequence-based scores are used to prioritize GWAS variants
   - Enformer/Borzoi for eQTL prediction and GWAS interpretation
   - van Lieshout et al. (medRxiv 2025) — PARM for somatic cancer driver identification
   - **Search specifically for**: Papers that apply sequence-based models to *germline* cancer risk variants (breast, prostate, liver). Papers that use Enformer/Borzoi/AlphaGenome to score PRS variants. Papers that combine sequence model predictions with GWAS fine-mapping (e.g., PolyFun, SuSiE, functionally-informed fine-mapping).

5. **Haplotype-Level and Combinatorial Variant Analysis (2023–2026)**:
   - **Search specifically for**: Has anyone used sequence-based models to predict effects of variant *combinations* (haplotypes) rather than single variants? This is the core novelty of the proposed project.
   - Papers on epistatic interactions in non-coding variants
   - Papers on haplotype-resolved expression prediction
   - Papers combining sequence models with population genetics (LD structure, selection)
   - The concept of "counterfactual haplotypes" — has this been explored?

### 2.2 Existing Approaches for Using Sequence Models to Score Disease Variants

For each approach, describe: the method, key findings, strengths, and limitations relevant to the proposed project.

**Approach 1: Single-Variant Scoring for Fine-Mapping**
- Using sequence model scores as priors in fine-mapping (e.g., PolyFun + Enformer, functionally-informed SuSiE)
- **Search for**: Weissbrod et al. (Nature Genetics 2020) PolyFun. Gazal et al. functional annotation for fine-mapping. Any papers combining PARM or AlphaGenome scores with fine-mapping tools.
- Relevance: This is the simplest way to use model predictions — score each GWAS variant individually.
- Limitation: Ignores combinatorial effects and haplotype structure.

**Approach 2: In Silico Saturated Mutagenesis (ISM) at Disease Loci**
- Systematically mutating every position around a disease-associated variant to understand the local regulatory grammar
- PARM paper demonstrates this for TERT promoter, CXCR4 promoter, etc.
- AlphaGenome paper demonstrates ISM for TAL1 oncogene, U2SURP splicing
- **Search for**: Published ISM analyses at breast cancer, prostate cancer, or HCC risk loci using any sequence model. Have FGFR2, CHEK2, 8q24, PNPLA3 loci been analyzed?

**Approach 3: Variant Effect Prediction for eQTL Interpretation**
- The PARM paper shows concordance with eQTL direction for fine-mapped GTEx v8 eQTLs (~72.9% concordance for top-ranked predictions)
- Borzoi: improved eQTL prediction over Enformer
- AlphaGenome: further improved (ρ = 0.49 coefficient, 0.80 sign auROC)
- **Search for**: Studies that compare model-predicted variant effects with measured eQTL effects specifically in cancer-relevant tissues (breast, liver, prostate). GTEx data availability for these tissues.

**Approach 4: Burden Testing with Model Scores**
- The van Lieshout et al. approach: aggregate model predictions across all variants in a region and test whether observed variants have more extreme predicted effects than background variants
- Two null models: "Alternative Alleles" (same position, different nucleotide change) and "Same Promoter" (same trinucleotide context, different position)
- This is a *region-level* test rather than a single-variant test. Relevant because PRS loci often harbor multiple causal variants.
- **Search for**: Other published burden-testing approaches that use sequence model scores. SKAT-type tests with deep learning features.

**Approach 5: Multimodal Variant Interpretation**
- AlphaGenome's cross-modality analysis: predicting that a variant simultaneously affects chromatin accessibility, histone marks, and expression
- The TAL1 oncogene example: three different mutation types (5' neo-enhancer, intronic SNV, 3' neo-enhancer) converge on TAL1 upregulation
- **Search for**: Other examples of multimodal variant interpretation at cancer risk loci. Has anyone systematically applied multimodal scoring to PRS variants?

### 2.3 The Missing Piece: Haplotype-Level Combinatorial Analysis

**This is the central novelty of the proposed project.** Provide a thorough analysis of what is and is not currently possible:

1. **The additivity assumption**: Most GWAS and PRS analyses assume that variant effects on risk are log-additive (multiplicative on the odds ratio scale). At the regulatory level, is this assumption valid? Search for:
   - Papers on regulatory variant epistasis in human promoters
   - MPRA studies that have tested combinations of variants (e.g., Tewhey et al., Cell 2016 — MPRA with multiple variants per construct)
   - The PARM paper's findings on TF motif–motif interactions: "a complex grammar of motif–motif interactions" — does this imply non-additivity?
   - Vaishnav et al. (Nature 2022) on yeast promoter engineering — combinatorial effects of mutations

2. **Computational feasibility of combinatorial prediction**: If a locus has N candidate variants, the number of possible haplotypes is 2^N. For N = 20, that's ~1 million combinations; for N = 30, ~1 billion. How to make this tractable:
   - The proposed iterative approach (score singles → select top K → score pairs → select top K pairs → etc.)
   - Greedy algorithms for combinatorial optimization
   - Alternative: use the model's gradient to identify synergistic variant combinations without exhaustive enumeration
   - **Search for**: Computational methods for exploring combinatorial sequence spaces with deep learning models. "Directed evolution" approaches using sequence models. The PARM paper's genetic algorithm for synthetic promoter design as a potential method.

3. **Linking predictions to real haplotypes**: The critical step of mapping predicted combinations to actually observed haplotypes in human populations. This requires:
   - Phased genotype data (knowing which variants are on the same chromosome)
   - Understanding of LD structure at each locus
   - **Search for**: Data sources with phased haplotypes at cancer risk loci: UK Biobank, 1000 Genomes, HGDP, TOPMed. What resolution and coverage do they provide for the specific PRS loci in breast/prostate/liver cancer?

### 2.4 Existing Benchmarks and Gold Standards

For each of the three cancer types (breast, liver/HCC, prostate), provide:

1. **The PRS models and their constituent SNPs**: From the Cancer Genetic Risk Panels reference document:
   - Breast: PRS313 (Mavaddat et al., 2019) — 313 SNPs. Also PRS77, subtype-specific scores.
   - Prostate: GRS451 (Wang et al., 2023) — 451 variants. PRS130 from BARCODE1 (McHugh et al., NEJM 2025). P-CARE with 601 variants.
   - HCC: PRS-5 (PNPLA3 + TM6SF2 + GCKR + MBOAT7 + HSD17B13). PRS-combined with 15 loci.

2. **SNPs that were associated in GWAS but excluded from PRS** (potential negative controls): These are variants that showed suggestive association (P < 5×10⁻⁶ but not genome-wide significant, or were significant but removed during LD clumping because they were tagging the same signal as a more significant variant). 
   - **Search for**: How to obtain these "near-miss" SNPs from GWAS summary statistics for breast/prostate/liver cancer. Are GWAS summary statistics publicly available from BCAC, PRACTICAL, and HCC GWAS consortia?
   - Also search for SNPs that were initially significant but later found to be population stratification artefacts — these would be ideal negative controls.

3. **Experimental validation data**: MPRA data at cancer risk loci, CRISPR perturbation data, allele-specific expression data.
   - **Search for**: Published MPRA studies at breast cancer risk loci (e.g., Grishin et al., Fachal et al.). MPRA data at prostate cancer risk loci (e.g., 8q24 region). Any MPRA data at HCC risk loci.
   - CRISPRi/CRISPRa data at cancer risk loci from ENCODE, Gasperini et al. (Cell 2019).

### 2.5 Population Genetics Resources for Haplotype Analysis

Provide a comprehensive inventory of data sources for the population-level validation step:

1. **UK Biobank**: ~500,000 individuals with genome-wide genotyping, imputed to ~97 million variants. Phased haplotypes available. Cancer phenotypes available (breast, prostate, liver cancer incidence). WGS data for ~200,000 participants. Access requirements and timelines.
   - **Search for**: Current UK Biobank data access policies. Is WGS data available for cancer-specific analyses? Sample sizes for each cancer type.

2. **1000 Genomes Project**: Phase 3 data with phased haplotypes for 2,504 individuals from 26 populations. Fully open access. Good for haplotype frequency estimation but no phenotype data.

3. **gnomAD v4**: Allele frequencies and haplotype information from >800,000 exomes and >76,000 genomes. Constraint metrics (o/e scores) useful for evaluating selection.
   - **Search for**: Does gnomAD provide haplotype-level data, or only allele frequencies? Can LD be estimated from gnomAD?

4. **TOPMed**: >180,000 individuals with deep WGS. Diverse ancestry. Phased. Access via dbGaP.

5. **FinnGen**: >500,000 Finnish individuals with genotyping + health records. Enriched for loss-of-function variants due to founder effects.

6. **Biobank Japan, China Kadoorie Biobank, African-ancestry biobanks**: Important for cross-ancestry validation, especially given that PRS transferability is a major issue.

7. **TCGA and ICGC/PCAWG**: Tumour WGS data. Used in van Lieshout et al. Limited to cancer patients.

**For each resource, specify**: sample size, available variants (array, WES, WGS), whether phased, whether cancer phenotypes are available, access mechanism, and estimated time to obtain access.

### 2.6 The Gap: What Has NOT Been Done

After the comprehensive search above, explicitly identify what has *not* been done before:

1. Has anyone used PARM to score *germline* disease-risk SNPs (as opposed to somatic mutations)?
2. Has anyone used any sequence model to predict *combinatorial* (multi-variant) effects on expression at disease loci?
3. Has anyone compared model-predicted "worst-case haplotypes" with observed haplotype frequencies to look for selection signals?
4. Has anyone used PARM + Borzoi/AlphaGenome in a two-stage design (fast local scan + slow long-range validation)?
5. Has anyone systematically tested PRS-included vs. PRS-excluded SNPs for predicted expression effect size differences?

For each gap: is this gap because (a) it's a genuinely new idea, (b) the models/data didn't exist until recently, or (c) it's been attempted but not published? Assess the novelty and feasibility.
## PART 3: DETAILED ANALYSIS OF THE PROPOSED EXPERIMENTAL FRAMEWORK

### 3.1 Overview of the Proposed Pipeline

The proposed pipeline has six major stages. For each stage, provide: (a) detailed technical specification, (b) alternative approaches that could replace it, (c) expected computational cost, (d) expected output and how to evaluate success, (e) potential failure modes and mitigations.

```
Stage 1: Curate disease loci and SNP panels
    ↓
Stage 2: Local ISM scanning with PARM (fast, 600 bp windows)
    ↓
Stage 3: Iterative combinatorial mutagenesis with PARM
    ↓
Stage 4: Long-range scoring of candidate haplotypes with Borzoi/AlphaGenome
    ↓
Stage 5: Map predicted haplotypes to observed haplotypes in population data
    ↓
Stage 6: Statistical analysis — validation, selection signals, counterfactuals
```

### 3.2 Stage 1: Curation of Disease Loci and SNP Panels

**Objective**: Define the exact genomic regions to analyze, the SNPs to include, and the positive/negative control sets.

**Sub-step 1a: Select target loci for each cancer type**

For breast cancer:
- Start with the PRS313 loci (Mavaddat et al., 2019). These 313 SNPs span 170+ genomic regions.
- For each SNP, define the analysis window. The proposed approach uses 1,400 bp windows around TSSs (van Lieshout approach). However, many PRS SNPs are *not* in promoters — they are in enhancers, introns, or intergenic regions.
- **Critical question**: How to handle non-promoter SNPs? PARM is specifically trained on promoter fragments. Options:
  - (i) Restrict analysis to the subset of PRS SNPs that fall within 1,400 bp of a TSS (~estimate: perhaps 20–30% of PRS313 SNPs). This limits scope but ensures PARM is used within its training domain.
  - (ii) Use PARM outside its training domain by centering windows on the SNP rather than the TSS. The PARM paper shows it can predict fragment activity for any genomic sequence, but the training data is promoter-enriched, so predictions for enhancer sequences may be less reliable.
  - (iii) Use Borzoi/AlphaGenome for non-promoter SNPs (they handle any genomic context) and reserve PARM for promoter-proximal SNPs.
  - **Recommendation**: Search for how many PRS313 SNPs fall within PARM's promoter windows. A mixed strategy (PARM for promoter SNPs, AlphaGenome for all SNPs) is likely optimal.

For prostate cancer:
- GRS451 (Wang et al., 2023) — 451 loci. LNCaP PARM model is available. LNCaP is an androgen-sensitive prostate cancer cell line, making it the most relevant available PARM model.
- The 8q24 region near MYC harbors multiple independent prostate cancer risk signals. This is a well-studied region that could serve as a showcase example.

For liver cancer (HCC):
- PRS-5 and PRS-combined (15 loci). Smaller number of loci but well-characterized.
- HepG2 PARM model is available. HepG2 is a hepatocellular carcinoma cell line — directly relevant.
- Key locus: PNPLA3 rs738409 (I148M) — the strongest single HCC risk variant. This is a coding variant (missense), so PARM is not the right tool for it. But the regulatory landscape around PNPLA3 includes non-coding variants in LD.

**Sub-step 1b: Define positive and negative control SNP sets**

*Positive controls (expect large predicted effects):*
- PRS-included SNPs for each cancer type
- Known functional variants with validated regulatory effects (e.g., TERT promoter mutations, FGFR2 regulatory variants in breast cancer)
- Fine-mapped eQTLs from GTEx in relevant tissues (breast → breast mammary tissue; prostate → prostate; liver → liver)

*Negative controls (expect small predicted effects):*
- **Type 1**: Random SNPs from the same genomic region matched for minor allele frequency, distance to nearest TSS, and LD structure — but not associated with disease. **Search for**: How to generate matched negative control SNP sets. Tools like SNPsnap (Pers et al., 2015).
- **Type 2**: SNPs that were initially suggestive in GWAS but excluded from PRS due to lack of replication, population stratification artifacts, or being in LD with a more significant variant. **Search for**: How to extract these from GWAS summary statistics. The BCAC, PRACTICAL, and HCC GWAS consortia provide full summary statistics.
- **Type 3**: Synonymous coding variants or deep intergenic variants far from any annotated regulatory element.

**Sub-step 1c: Annotate each SNP with genomic context**
- Distance to nearest TSS, nearest CTCF site, nearest enhancer (from ENCODE cCREs)
- Chromatin state in relevant cell type (from Roadmap Epigenomics, ENCODE)
- Known eQTL association in GTEx (tissue-specific)
- Allele frequency across populations (gnomAD)
- LD structure (R² with other PRS SNPs and nearby variants)
- Whether the SNP disrupts a known TF binding motif (using HOCOMOCO or JASPAR motif databases)

### 3.3 Stage 2: Local ISM Scanning with PARM

**Objective**: For each locus, systematically predict the effect of every possible single nucleotide change in the promoter region using PARM.

**Technical specification**:
- For each promoter region (1,400 bp), slide a 600 bp window with a step of 50 bp → 17 overlapping windows per promoter region.
- In each window, perform ISM: for each of the 600 positions, predict activity for the reference allele and all 3 alternative alleles → 600 × 3 = 1,800 predictions per window.
- For overlapping positions (covered by multiple windows), average the ISM scores.
- Use the cell-type-appropriate PARM model: MCF7 for breast cancer, HepG2 for HCC, LNCaP for prostate cancer.

**Output**: An "importance score" at every position = mean(reference activity) − mean(mutant activities). Positive = wild-type nucleotide contributes positively to promoter activity. Negative = mutations enhance activity.

**Key metric**: For each PRS SNP that falls within the window, the predicted expression delta (alternative allele activity − reference allele activity). This is the single-SNP predicted effect.

**Alternative approaches to consider**:
1. **Gradient-based attribution instead of ISM**: Instead of scoring all 3 mutations at each position, compute the gradient of the output with respect to the one-hot input. Much faster (one forward + backward pass per sequence) but provides a linearized approximation. Search for: How well do gradient methods approximate ISM for PARM specifically? The PARM paper does not compare these methods.
2. **Using AlphaGenome ISM instead of PARM ISM**: AlphaGenome's ISM provides multimodal output (expression + chromatin + TF binding) at base-pair resolution from 1 Mb context. More informative but requires API access and may have rate limits. For the initial scan, PARM's speed advantage (435 vs. ~1 var/sec) is substantial.
3. **Using pre-computed ISM scores**: The PARM interactive browser (http://parm.deridderlab.nl) provides ISM for all 30,607 human promoters. Check if the cancer-relevant PRS loci are already computed there.

**Expected results and validation**:
- For known functional variants (e.g., TERT −124 C>T, −146 C>T), PARM should predict large positive delta scores. The PARM paper confirms this.
- For PRS SNPs in general, we expect a distribution of predicted effects. The key test: is this distribution shifted relative to the negative control SNPs?
- **Statistical test**: Wilcoxon rank-sum test comparing predicted |delta| for PRS SNPs vs. negative control SNPs. Also compare distributions of delta direction (activating vs. repressive) — PRS SNPs may show directional consistency with known oncogene/TSG biology.

### 3.4 Stage 3: Iterative Combinatorial Mutagenesis with PARM

**Objective**: Identify combinations of mutations within each promoter that have synergistic (non-additive) effects on predicted expression.

**The proposed iterative algorithm**:
```
1. Run ISM → select top K₁ single mutations with largest |delta|
2. For each pair of top K₁ mutations: predict activity with both mutations present
3. Compute "interaction score" = actual_double_delta − (delta_A + delta_B)
   (If interaction > 0: synergistic; if < 0: antagonistic; if ≈ 0: additive)
4. Select top K₂ pairs with largest |interaction| or largest |total delta|
5. For each top K₂ pair, add each remaining top K₁ single → predict triples
6. Iterate until convergence or computational budget exhausted
```

**Critical considerations**:

1. **Additivity vs. non-additivity in PARM**: The PARM paper demonstrates complex motif–motif interactions and position-dependent TF effects. This strongly suggests non-additive effects should be detectable. However, CNNs may have limited ability to model interactions between distant positions within the input. Given PARM's 600 bp window, interactions within ~500 bp should be captured.

2. **Window limitation**: PARM takes 600 bp input. If two variants are >600 bp apart, they cannot be scored together in a single PARM call. Options:
   - (i) Only test combinations within the same 600 bp window. This limits analysis to promoter-proximal combinations.
   - (ii) Use overlapping windows and stitch scores together under an additivity assumption for cross-window effects.
   - (iii) **Use Borzoi/AlphaGenome for cross-window combinations** (they handle much longer sequences). Reserve PARM for within-window combinatorics only.

3. **Combinatorial explosion management**: With K₁ = 20 top single mutations per window:
   - Pairs: C(20, 2) = 190 — very feasible
   - Triples: C(20, 3) = 1,140 — feasible
   - Quadruples: C(20, 4) = 4,845 — feasible
   - Beyond 4-way: may need greedy selection or genetic algorithm approaches
   
   **Alternative**: Adapt the PARM paper's genetic algorithm for synthetic promoter design. Instead of starting from random sequences and evolving toward high activity, start from the reference sequence and evolve toward maximum or minimum activity by mutating only at positions corresponding to known or candidate variants. This is more principled than exhaustive enumeration.

4. **What counts as a "mutation"**: The proposed approach tests all possible single nucleotide changes. But for disease variants, we care specifically about the known alternative alleles at GWAS/PRS loci. So the combinatorial analysis should specifically combine the known risk alleles, not arbitrary mutations.

**Search for**: Has anyone used genetic algorithms or directed evolution with sequence-based models to explore combinatorial variant effects? The Vaishnav et al. (Nature 2022) yeast promoter engineering study is relevant — how did they handle combinatorial effects? Also search for Gosai et al. (Nature 2024) on machine-guided design of cis-regulatory elements.

### 3.5 Stage 4: Long-Range Scoring with Borzoi/AlphaGenome

**Objective**: Score the candidate haplotypes from Stage 3 using models that capture long-range context and distal regulatory effects.

**Why this stage is necessary**: PARM predicts autonomous promoter activity without distal enhancer effects. A haplotype may contain variants that individually affect promoter activity (captured by PARM) but also variants in distal enhancers that modulate expression through 3D chromatin interactions (captured by Borzoi/AlphaGenome).

**Technical specification for Borzoi scoring**:
- Input: 524,288 bp sequence centered on the gene of interest
- Introduce all haplotype variants simultaneously into the input sequence
- Predict RNA-seq coverage tracks for the relevant tissue
- Score: sum of predicted RNA-seq coverage over the gene body, comparing reference vs. haplotype
- Repeat for each candidate haplotype

**Technical specification for AlphaGenome scoring**:
- Input: 1 Mb sequence centered on the gene
- Introduce haplotype variants
- Predict RNA-seq coverage (for expression), ATAC-seq (for chromatin accessibility), histone marks (for regulatory state)
- Multimodal scoring: assess whether the predicted expression change is consistent with predicted chromatin changes
- Advantage: can detect mechanism (e.g., variant disrupts an enhancer → reduced H3K27ac → reduced expression)

**Critical question: How to introduce multiple variants simultaneously?**
- For Borzoi: modify the one-hot encoded input sequence at all variant positions. Straightforward.
- For AlphaGenome: same approach, but need to ensure the API supports multi-variant input (or manually construct the alternative sequence). **Search for**: AlphaGenome API documentation on multi-variant scoring.
- **Potential issue**: Models are trained on single-genome reference sequences. Introducing many variants simultaneously (e.g., 10–20 in a 500 kb window) creates a sequence that may be far from training distribution. This is analogous to the "out-of-distribution intervention" problem in mechanistic interpretability. How to assess whether model predictions remain reliable for multi-variant haplotypes? **Search for**: Any studies on reliability of sequence model predictions for sequences with many variants. Avsec et al. (AlphaGenome) test indel variant effects — how many simultaneous changes were tested?

### 3.6 Stage 5: Mapping Predicted Haplotypes to Population Data

**Objective**: Determine which of the predicted "expression-altering haplotypes" actually exist in human populations, at what frequency, and whether they are associated with disease.

**Sub-step 5a: Extract observed haplotypes at target loci**

For each target locus, from phased population data (UK Biobank, 1000 Genomes):
- Identify all common and rare variants within the analysis window
- Construct observed haplotypes (phased allele combinations)
- Calculate haplotype frequencies per population
- **Critical issue**: Phasing accuracy decreases for rare variants and variants far from genotyped markers. For WGS data (UK Biobank ~200K), phasing is statistical, not experimental (except for trios or read-backed phasing).
- **Search for**: Tools for extracting and analyzing haplotypes from phased VCF files. SHAPEIT5, Eagle2, phasing accuracy estimates at different allele frequencies.

**Sub-step 5b: Score observed haplotypes**

For each observed haplotype:
1. Construct the haplotype sequence by introducing all variants into the reference
2. Score with PARM (for promoter region) and/or Borzoi/AlphaGenome (for full locus)
3. Compute predicted expression level relative to reference

**Sub-step 5c: Construct theoretical haplotype distributions**

Generate distributions of predicted expression for:
- **Observed haplotypes**: weighted by their population frequency
- **All possible single-variant haplotypes**: each with exactly one variant (for comparison with single-SNP PRS assumptions)
- **Maximally deleterious/activating haplotypes**: the theoretical worst-case from Stage 3 combinatorial analysis
- **Random haplotypes**: randomly combining variants without regard to LD structure (to estimate the "null" expectation if variant co-occurrence were random)

**Sub-step 5d: Assign individuals to haplotype bins**

The proposed approach: assign each individual to the observed haplotype containing the most expression-altering variants. This requires a principled definition:
- **Option A (proposed)**: For each individual's haplotype, count the number of variants that are also in the "maximally deleterious" predicted haplotype. Assign to bin = count.
- **Option B**: Score each individual's actual haplotype with Borzoi/AlphaGenome and use the continuous predicted expression value directly. This avoids arbitrary binning and is statistically more powerful.
- **Option C**: Use a hierarchical approach — first cluster haplotypes by similarity, then score cluster representatives. This reduces computation.
- **Recommendation**: Option B is superior because it uses the model's continuous predictions rather than discrete counting, and it naturally accounts for the fact that different variants contribute different effect sizes.

### 3.7 Stage 6: Statistical Analysis

**Analysis 6a: PRS SNPs vs. negative controls — predicted effect size distributions**

- **Hypothesis**: PRS-included SNPs have larger |predicted expression deltas| than PRS-excluded/negative control SNPs.
- **Test**: Two-sample Kolmogorov-Smirnov test or Wilcoxon rank-sum test comparing |delta| distributions.
- **Expected effect size**: Based on the PARM eQTL concordance (~73% for top-ranked variants), the signal should be present but not overwhelming. The van Lieshout et al. study found that cancer driver gene promoters had significantly lower p-values than other genes (Wilcoxon p = 1.49 × 10⁻³ even excluding TERT).
- **Multiple testing**: If testing across three cancer types × two models (PARM, Borzoi) × two control sets = 12 tests, Bonferroni threshold = 0.05/12 = 0.004.

**Analysis 6b: Predicted haplotype expression vs. disease status**

- **Hypothesis**: Individuals with haplotypes predicted to have more extreme expression levels (very high for oncogenes, very low for tumor suppressors) are more likely to have cancer.
- **Test**: Logistic regression with cancer status as outcome and predicted haplotype expression score as predictor, adjusting for age, sex, ancestry PCs, and other risk factors.
- **Data requirement**: UK Biobank with linked cancer registry data. Estimated sample sizes: ~15,000 breast cancer cases, ~10,000 prostate cancer cases, ~1,500 liver cancer cases among ~500K participants.
- **Power analysis**: **Search for**: Estimated per-allele odds ratios for PRS-included SNPs. For breast cancer PRS313, typical per-SNP ORs range from 1.01 to 1.5. If predicted expression scores aggregate multiple variant effects, the composite score should have a larger OR. Estimate power for detecting OR = 1.1 with 15,000 cases and 485,000 controls.

**Analysis 6c: Selection signal analysis**

- **Hypothesis**: The most extreme predicted haplotypes (highest predicted expression for oncogenes, lowest for tumor suppressors) are observed less frequently than expected under neutrality.
- **Approach 1**: Compare observed haplotype frequency with expected frequency under random assortment of alleles (ignoring LD). If the observed frequency of the "worst" haplotype is much lower than expected from individual allele frequencies, this suggests negative selection or incompatibility.
- **Approach 2**: Use population genetics tools to estimate selection coefficients at haplotype level. **Search for**: Methods for detecting selection on regulatory haplotypes. SDS (Singleton Density Score), iHS (integrated haplotype score), nSL. Can these be applied at the resolution of individual promoter regions?
- **Approach 3**: Compare across populations. If a predicted-deleterious haplotype is absent in populations with low incidence of the cancer type but present in high-incidence populations, this provides evidence for population-specific selection or drift.
- **Caution**: Most PRS variants have small individual effects (OR 1.01–1.1). The selection coefficient on regulatory haplotypes may be too small to detect with current methods unless the haplotype combines many variants with consistent directional effects. **Calculate**: If a haplotype combines 10 risk alleles each with OR 1.05, the combined OR under multiplicativity is 1.05¹⁰ ≈ 1.63. A selection coefficient against this haplotype would be very small (s << 0.01) and likely undetectable.

**Analysis 6d: Concordance between predicted expression effects and known biology**

For each locus where the model predicts a large effect:
- Does the predicted direction (up/down) match the known role of the gene? (Oncogene upregulation or tumor suppressor downregulation = consistent with risk.)
- Does the predicted tissue specificity match? (e.g., does the HepG2 PARM model predict larger effects for HCC loci than the MCF7 model?)
- Are the predicted TF motifs disrupted consistent with known cancer-relevant TFs?
## PART 4: SPECIFIC HYPOTHESES, EXPERIMENTAL PROTOCOLS, AND CRITICAL GAPS

### 4.1 Testable Hypotheses

For each hypothesis below, provide: (H) the hypothesis statement, (H₀) the null hypothesis, (P) the experimental protocol, (E+) the expected result if the hypothesis is true, (E−) the expected result if it is false, (C) what you would conclude in each case, and (D) the data sources required.

---

**Hypothesis 1: PRS-included SNPs have larger predicted expression effects than matched non-PRS SNPs**

- **(H)**: SNPs included in validated PRS models (PRS313 for breast, GRS451 for prostate, PRS-5/PRS-combined for HCC) have significantly larger absolute predicted expression deltas (|Δactivity|) from PARM ISM than MAF-matched, distance-to-TSS-matched SNPs that are not in the PRS.
- **(H₀)**: There is no difference in predicted expression effects between PRS and non-PRS SNPs.
- **(P)**: (1) Run PARM ISM at all promoter windows containing PRS SNPs using cell-type-matched models (MCF7 for breast PRS313, LNCaP for prostate GRS451, HepG2 for HCC PRS). (2) Generate matched negative control SNPs using SNPsnap or a custom matching algorithm. (3) Run PARM ISM at the same promoter windows for control SNPs. (4) Compare |Δactivity| distributions using Wilcoxon rank-sum test.
- **(E+)**: PRS SNPs show significantly larger |Δactivity| (p < 0.004 after Bonferroni correction). Expected AUC for discriminating PRS vs. non-PRS: 0.55–0.65 (modest, since most PRS SNPs are tagging variants, not causal).
- **(E−)**: No significant difference. This would mean either (a) PARM cannot distinguish functional from non-functional variants at this level, or (b) most PRS SNPs exert effects via distal enhancers that PARM's promoter-focused 600 bp window cannot capture.
- **(C)**: If positive, establishes basic validation that PARM captures disease-relevant regulatory variation. If negative, pivot to using AlphaGenome/Borzoi (longer range, multimodal) as the primary model for subsequent stages.
- **(D)**: PRS variant lists from published studies. GWAS summary statistics for generating matched controls. PARM pre-trained models.

---

**Hypothesis 2: Multi-model concordance identifies high-confidence functional variants**

- **(H)**: PRS SNPs for which PARM, Borzoi, and AlphaGenome *all* predict expression effects in the same direction are more likely to be fine-mapped causal variants (high posterior inclusion probability in eQTL studies) than SNPs with discordant predictions.
- **(H₀)**: Model concordance does not correlate with causal variant status.
- **(P)**: (1) Score all PRS SNPs with PARM, Borzoi, and AlphaGenome. (2) Define concordant set: same sign of predicted effect across all three models. Discordant set: mixed signs. (3) Cross-reference with fine-mapped eQTL data from GTEx v8 (SuSiE PIP > 0.5 = high-confidence causal). (4) Test whether concordant SNPs are enriched for high PIP using Fisher's exact test.
- **(E+)**: Concordant SNPs are 2–4× enriched for high PIP relative to discordant SNPs.
- **(E−)**: No enrichment. Suggests models are capturing different (or complementary) aspects of regulation.
- **(C)**: If positive, establishes a multi-model ensemble strategy for variant prioritization. If negative, investigate *which* model best correlates with causal status — this is independently valuable.
- **(D)**: GTEx v8 fine-mapped eQTLs (publicly available). Model predictions from all three models.

---

**Hypothesis 3: PARM detects non-additive (epistatic) interactions between nearby regulatory variants**

- **(H)**: For pairs of variants within the same 600 bp PARM window, the predicted joint effect (Δactivity with both variants present) differs from the sum of individual effects (ΔA + ΔB) in at least 10% of tested pairs.
- **(H₀)**: All variant effects are additive within PARM's prediction framework.
- **(P)**: (1) For each target locus, identify all common variants (MAF > 1%) within promoter windows. (2) Run PARM for: reference, variant A only, variant B only, variants A+B together. (3) Compute interaction score: I = Δ(A+B) − (ΔA + ΔB). (4) Test whether the distribution of I scores is significantly different from zero using a one-sample t-test or Wilcoxon signed-rank test.
- **(E+)**: Significant non-zero interaction scores for >10% of pairs, with largest interactions at pairs of variants that occupy different TF motifs (consistent with PARM's learned motif–motif grammar).
- **(E−)**: Nearly all interactions ≈ 0. This would suggest PARM's variant effects are approximately additive within promoter windows, simplifying the combinatorial analysis.
- **(C)**: If non-additive effects are common, the combinatorial analysis (Stage 3) is essential and cannot be replaced by summing single-variant scores. If additive, single-variant scores suffice and the combinatorial stage can be simplified or skipped.
- **(D)**: Phased genotype data to identify co-occurring variants. PARM models.

---

**Hypothesis 4: Predicted "worst-case" haplotypes are depleted in healthy populations**

- **(H)**: For cancer-relevant loci (especially tumor suppressor genes), the haplotype with the most extreme predicted expression reduction is observed at a lower frequency than expected from individual allele frequencies under linkage equilibrium.
- **(H₀)**: Extreme haplotype frequencies match expectations from allele frequency products (no evidence of selection or synthetic lethality).
- **(P)**: (1) For each target TSG locus, identify the top-5 most expression-reducing variants from PARM ISM. (2) From phased 1000 Genomes data, calculate the observed frequency of the haplotype carrying all 5 risk alleles. (3) Calculate the expected frequency assuming independence: f_expected = ∏f_i where f_i is the frequency of each risk allele. (4) Test whether f_observed < f_expected using a binomial test.
- **(E+)**: Observed frequency significantly below expected for ≥3 loci (after multiple testing correction). Expected effect: 2–10× depletion for the most extreme haplotypes.
- **(E−)**: No depletion. This could mean: (a) selection against regulatory haplotypes is too weak to detect, (b) the variants are in strong LD such that the expected frequency is already low, or (c) the PARM-predicted "worst-case" haplotype doesn't actually cause a biologically meaningful expression change.
- **(C)**: If positive, provides evidence for purifying selection on regulatory haplotypes and validates that the model's predictions are biologically consequential at the population level. If negative, investigate whether LD alone explains the pattern, and whether the selection signal is detectable with larger samples.
- **(D)**: 1000 Genomes Phase 3 phased data. UK Biobank phased data (larger sample = more power for rare haplotypes).

---

**Hypothesis 5: Cell-type-specific PARM models predict cancer-type-specific risk**

- **(H)**: The PARM model trained on the cancer-relevant cell type (MCF7 for breast, LNCaP for prostate, HepG2 for HCC) predicts larger expression effects for the corresponding cancer's PRS SNPs than PARM models trained on non-relevant cell types.
- **(H₀)**: Cell type of the PARM model does not affect the magnitude of predicted effects at cancer-specific PRS SNPs.
- **(P)**: (1) Run all 9 available PARM models on the PRS SNPs for all three cancer types. (2) For each cancer type, compare the mean |Δactivity| predicted by the matched cell-type model vs. all unmatched models. (3) Test using a paired Wilcoxon test or linear mixed model.
- **(E+)**: Matched models produce significantly larger predicted effects (e.g., MCF7 model predicts larger effects for breast PRS SNPs than K562, HCT116, etc. models). Expected fold-enrichment: 1.2–1.5×.
- **(E−)**: No cell-type specificity. This would suggest that cancer risk variants act through cell-type-invariant regulatory mechanisms (consistent with PARM's finding that promoter activities are correlated R = 0.78–0.95 across cell types, though there are cell-type-specific regulators).
- **(C)**: If positive, validates the rationale for using cell-type-specific models and may identify cancer-type-specific regulatory mechanisms at risk loci. If negative, a single PARM model may suffice, simplifying the pipeline.
- **(D)**: All PARM pre-trained models. PRS variant lists for three cancer types.

---

**Hypothesis 6: Borzoi/AlphaGenome capture distal enhancer effects that PARM misses**

- **(H)**: For PRS SNPs located >1 kb from the nearest TSS (i.e., outside PARM's effective window), Borzoi and AlphaGenome predict significantly larger expression effects than for random non-PRS SNPs at similar distances, while PARM predictions are at chance.
- **(H₀)**: Neither model distinguishes PRS from non-PRS SNPs at distal positions.
- **(P)**: (1) Stratify PRS SNPs by distance to nearest TSS: proximal (<500 bp), intermediate (500 bp – 5 kb), distal (>5 kb). (2) Score each stratum with PARM, Borzoi, and AlphaGenome. (3) Compare PRS vs. non-PRS |Δexpression| within each distance stratum for each model.
- **(E+)**: PARM discriminates PRS vs. non-PRS only at proximal distances. Borzoi/AlphaGenome discriminate at all distances, with particular advantage at distal positions.
- **(E−)**: All models fail at distal positions. This would highlight a fundamental limitation of current sequence models for distal variant interpretation.
- **(C)**: Establishes the complementary value of promoter-focused (PARM) and long-range (Borzoi/AlphaGenome) models, and identifies the optimal model for each genomic context.
- **(D)**: PRS variant lists annotated with distance to nearest TSS. All model predictions.

---

### 4.2 Critical Gaps and How to Address Them

**Gap 1: PARM is trained on promoter fragments — most PRS SNPs are not in promoters**

- *Problem*: The PRS313 for breast cancer contains 313 SNPs spanning 170+ loci. Based on GWAS architecture, ~80% of risk variants are in non-coding regions, many in distal enhancers or intergenic regions far from any TSS.
- *Estimated impact*: Only ~30–50 of 313 PRS SNPs may fall within PARM promoter windows. The rest are inaccessible to PARM.
- *Solution*: (a) Use PARM for the promoter-proximal subset and Borzoi/AlphaGenome for all SNPs. (b) Focus the PARM combinatorial analysis on loci with multiple proximal variants (e.g., dense promoter-region haplotypes). (c) Consider that the van Lieshout et al. study successfully used PARM for promoter-level analysis even though many cancer drivers act through non-promoter mechanisms.
- **Search for**: What fraction of PRS313, GRS451, and PRS-5 SNPs are within 1 kb of a TSS? This determines the scope of PARM-based analysis.

**Gap 2: Models are trained on reference genome sequences — haplotype-level predictions may be out-of-distribution**

- *Problem*: Introducing 10+ variants into a 500 kb sequence creates a sequence that has never been seen during training. The model's behavior on such inputs is unknown.
- *Estimated impact*: For common variants (MAF > 5%), the model has likely seen similar sequences in the training data (since the training genome is a reference but MPRA/RNA-seq data comes from cell lines with their own genotypes). For rare variants or extreme combinations, OOD effects are possible.
- *Solution*: (a) Validate against known multi-variant effects from MPRA data (e.g., Tewhey et al. tested haplotype-level effects). (b) Test model uncertainty: do predictions become less confident for sequences with many variants? (c) Use ensemble disagreement (PARM 5-fold cross-validation models) as an uncertainty measure. (d) Start with low-order combinations (2–3 variants) before attempting higher-order.
- **Search for**: Any studies on how sequence-based model predictions degrade as more variants are introduced simultaneously. OOD detection methods for genomic sequence models.

**Gap 3: Haplotype phasing uncertainty**

- *Problem*: Phasing from array or WGS data is statistical, not experimental. For rare variants, phasing error rates can be 5–20%. This means that some "observed haplotypes" are actually mis-phased.
- *Estimated impact*: Mainly affects rare haplotypes (those combining rare variants). Common PRS SNPs in strong LD will be phased correctly with >99% accuracy.
- *Solution*: (a) Focus on common variants (MAF > 1%) where phasing is reliable. (b) Use trio data from family studies for validation. (c) Use read-backed phasing from WGS data where possible. (d) Perform sensitivity analysis: how much does the result change if X% of haplotypes are mis-phased?
- **Search for**: Phasing accuracy estimates from UK Biobank WGS data (Halldorsson et al., Nature 2022). SHAPEIT5 phasing error rates by MAF and distance.

**Gap 4: Lack of ground truth for combinatorial expression effects**

- *Problem*: There is no large-scale dataset of experimentally measured *combinatorial* variant effects on expression in cancer-relevant tissues. Individual eQTLs are available from GTEx, but haplotype-level eQTLs have barely been studied.
- *Estimated impact*: Cannot directly validate whether PARM-predicted haplotype effects are accurate. Must rely on indirect validation (e.g., association with disease status, consistency with selection signals).
- *Solution*: (a) Use allele-specific expression (ASE) data as a proxy — ASE measures the expression difference between maternal and paternal haplotypes within the same cell. **Search for**: ASE data in cancer-relevant tissues from GTEx, TCGA. (b) Design a targeted MPRA experiment to test specific predicted haplotype combinations — this could be a follow-up experimental validation. (c) Look for natural experiments: individuals homozygous for the predicted "bad" haplotype vs. heterozygous vs. homozygous reference.

**Gap 5: The selection signal may be too weak to detect**

- *Problem*: Common cancer risk variants individually have small effects (OR 1.01–1.1). Even combining 10 such variants yields a modest combined effect. The selection coefficient against such a haplotype is negligible for post-reproductive cancers (breast, prostate, liver cancers typically occur after age 50).
- *Estimated impact*: Selection signals may be undetectable for most cancer risk haplotypes, unless the variants also affect fitness-relevant traits before reproductive age.
- *Solution*: (a) Focus on loci where the combined haplotype effect is predicted to be large (>2-fold expression change). (b) Test for selection signals using the most powerful available methods (iHS, nSL) with the largest available datasets. (c) Consider alternative explanations for haplotype depletion: genetic drift, population bottlenecks, or synthetic associations. (d) **Search for**: Are cancer risk variants also associated with reproductive fitness traits? If a breast cancer PRS SNP also affects puberty timing or fertility, the selection signal would be stronger.

**Gap 6: Confounding by linkage disequilibrium**

- *Problem*: The PRS SNPs are typically tag SNPs, not causal variants. The true causal variant may be a different SNP in LD with the tag. PARM may predict a small effect for the tag SNP but a large effect for the (ungenotyped or unidentified) causal variant nearby.
- *Estimated impact*: Hypothesis 1 may underestimate the true discriminative power of the models because the "positive" set (PRS SNPs) includes many non-causal tag SNPs.
- *Solution*: (a) Where available, use fine-mapped variants (high PIP from SuSiE/FINEMAP) instead of tag SNPs. (b) Run ISM across the full LD block surrounding each tag SNP and identify the variant with the largest predicted effect — if this differs from the tag SNP, it may be the causal variant. This is an additional valuable output of the project. (c) **Search for**: Fine-mapped causal variants for breast/prostate/HCC GWAS loci from recent studies (e.g., the breast cancer fine-mapping by Fachal et al., Nature Genetics 2020).

### 4.3 Negative Control Experiments

**Negative Control 1: Shuffled sequences**
- For each target promoter, shuffle the sequence (preserving dinucleotide frequencies) and run PARM ISM. The distribution of |Δactivity| should be a baseline for what the model predicts on non-biological sequence. PRS SNP effects should be significantly above this baseline.

**Negative Control 2: Known neutral variants**
- Score a set of common synonymous coding variants (which do not affect regulatory elements) with PARM. These should have near-zero predicted effects.

**Negative Control 3: Random variant combinations**
- For the combinatorial analysis: randomly combine variants across different chromosomes (where no LD or biological interaction exists). Score these "pseudo-haplotypes" with Borzoi/AlphaGenome. These should show no enrichment for extreme predicted effects.

**Negative Control 4: Permutation test for selection signals**
- Randomly reassign disease status labels across individuals and repeat the haplotype-disease association analysis. This provides the null distribution for testing the significance of haplotype effects.

### 4.4 Additional Research Questions Worth Investigating

If the core analyses succeed, the following extensions would strengthen the project:

1. **Cross-ancestry analysis**: Do the same predicted haplotypes confer risk across ancestries? This is directly relevant to the PRS transferability problem. Use 1000 Genomes multi-ancestry data.

2. **Tissue-specificity of predicted effects**: For each locus, run all 9 PARM models and characterize which loci show tissue-specific vs. tissue-invariant predicted effects. Compare with tissue-specific eQTL data from GTEx.

3. **Comparison with experimental MPRA at cancer risk loci**: If published MPRA data exists for specific cancer risk loci (search for this), directly validate PARM's ISM predictions against measured allelic effects.

4. **Drug target identification**: For loci where the model predicts that a variant creates or destroys a specific TF binding site, assess whether the TF is druggable. This connects sequence model predictions to potential therapeutic interventions.

5. **Comparison of PARM motif annotations with cancer GWAS enrichments**: The PARM paper identifies TF families active in each cell type. Compare these with TF motif enrichments from cancer GWAS (e.g., LDSC-SEG analyses showing which chromatin features are enriched for cancer heritability).
## PART 5: SYNTHESIS AGENT — PRIORITIZED FIVE-MONTH RESEARCH PLAN

**You are now the Synthesis Agent.** Take all of the above research and produce a prioritized, time-bound, five-month research plan. Use the following prioritization criteria:

1. **Simplicity**: How easy is this experiment to implement? (Score 1–5, 5 = very easy)
2. **Yield**: How much insight does this experiment provide? (Score 1–5, 5 = transformative)
3. **Risk**: What is the probability of a useful result? (Score 1–5, 5 = near certain)
4. **Dependencies**: Does this experiment depend on the results of another? If so, which?
5. **Novelty**: How novel is this analysis? (Score 1–5, 5 = completely unprecedented)

**Compute a Priority Score = (Yield × Risk × Novelty) / (6 − Simplicity)** and rank all experiments.

### Proposed Experiment Inventory

Before generating the timeline, score and rank ALL of the following experiments:

| ID | Experiment | Simplicity | Yield | Risk | Novelty | Dependencies | Priority Score |
|----|-----------|------------|-------|------|---------|-------------|----------------|
| E1 | Curate PRS variant panels + matched controls for breast/prostate/HCC | 4 | 3 | 5 | 1 | None | — |
| E2 | PARM ISM at all promoter-proximal PRS SNPs (3 cancer types × matched model) | 4 | 4 | 4 | 3 | E1 | — |
| E3 | Compare |Δ| distributions: PRS vs. controls (Hypothesis 1) | 5 | 4 | 4 | 2 | E2 | — |
| E4 | Cell-type specificity analysis (Hypothesis 5) — all 9 PARM models on all 3 cancer PRS sets | 4 | 3 | 3 | 3 | E1 | — |
| E5 | Score all PRS SNPs with Borzoi (or AlphaGenome if API available) | 3 | 4 | 4 | 2 | E1 | — |
| E6 | Multi-model concordance analysis (Hypothesis 2) — PARM + Borzoi + AlphaGenome vs. eQTL PIP | 3 | 5 | 3 | 4 | E2, E5 | — |
| E7 | Distance-stratified analysis (Hypothesis 6) — proximal vs. distal SNP effects per model | 3 | 4 | 4 | 3 | E2, E5 | — |
| E8 | PARM combinatorial mutagenesis — pairs and triples within promoter windows | 3 | 5 | 3 | 5 | E2 | — |
| E9 | Non-additivity analysis (Hypothesis 3) — quantify epistatic interactions | 3 | 4 | 3 | 5 | E8 | — |
| E10 | Score candidate haplotypes with Borzoi/AlphaGenome (Stage 4) | 2 | 5 | 3 | 5 | E8 | — |
| E11 | Extract observed haplotypes from 1000 Genomes / UK Biobank at target loci | 3 | 3 | 4 | 3 | E1 | — |
| E12 | Score observed haplotypes with models (Stage 5b) | 2 | 4 | 3 | 4 | E10, E11 | — |
| E13 | Haplotype frequency analysis — observed vs. expected (Hypothesis 4) | 3 | 5 | 2 | 5 | E12 | — |
| E14 | Haplotype-disease association in UK Biobank (Analysis 6b) | 2 | 5 | 2 | 5 | E12 | — |
| E15 | Selection signal analysis using iHS/nSL (Analysis 6c) | 2 | 4 | 2 | 5 | E13 | — |
| E16 | ISM-based fine-mapping: identify predicted causal variant at each PRS LD block | 3 | 5 | 4 | 3 | E2 | — |
| E17 | Validate against published MPRA data at cancer risk loci (if available) | 3 | 4 | 3 | 2 | E2 | — |
| E18 | Cross-ancestry haplotype analysis using 1000 Genomes multi-ancestry data | 2 | 4 | 3 | 4 | E13 | — |
| E19 | Negative control experiments (shuffled sequences, neutral variants, random haplotypes) | 4 | 3 | 5 | 1 | E2 | — |
| E20 | TF motif annotation of predicted functional variants using PARM RS analysis | 3 | 4 | 4 | 3 | E2 | — |

**Calculate the Priority Scores and rank all experiments from highest to lowest priority.** Then map them onto the five-month timeline below.

---

### Month 1: Foundation & Quick Wins (highest priority, no dependencies)

**Objective**: Set up infrastructure, curate data, and run the fastest high-value experiments.

**Week 1–2: Data curation and infrastructure**
- [ ] E1: Curate PRS variant panels for breast (PRS313), prostate (GRS451), and HCC (PRS-5/PRS-combined)
- [ ] Download and annotate all PRS SNPs with genomic context (distance to TSS, chromatin state, eQTL status)
- [ ] Generate matched negative control SNP sets using SNPsnap or custom matching
- [ ] Set up PARM (clone https://github.com/vansteensellab/PARM, install dependencies, verify models load)
- [ ] Set up Borzoi inference pipeline (or alternative: set up AlphaGenome API access)
- [ ] Download 1000 Genomes Phase 3 phased data for target loci
- **Deliverables**: Curated SNP lists with annotations. Working PARM and Borzoi/AlphaGenome pipelines. Matched control SNP sets.
- **Person-hours**: ~60 hours
- **Compute**: Minimal (data processing)

**Week 2–4: PARM ISM scan and basic validation**
- [ ] E2: Run PARM ISM at all promoter-proximal PRS SNPs using cell-type-matched models
- [ ] E19: Run negative control experiments (shuffled sequences, neutral variants)
- [ ] E3: Compare |Δ| distributions for PRS vs. control SNPs (Hypothesis 1)
- [ ] E4: Run all 9 PARM models on all PRS sets to test cell-type specificity (Hypothesis 5)
- **Deliverables**: ISM scores for all PRS SNPs. Statistical test results for Hypothesis 1 and 5. First visualization: distributions of predicted effects for PRS vs. controls.
- **Person-hours**: ~80 hours
- **Compute**: ~10 GPU-hours (PARM ISM is fast)
- **Go/no-go decision**: If PRS SNPs do NOT show significantly larger predicted effects than controls (Hypothesis 1 fails), reassess whether PARM is the right model for this project. Consider switching primary model to Borzoi/AlphaGenome.

---

### Month 2: Core Single-SNP Analysis with Multiple Models

**Objective**: Score all SNPs with all available models and identify the most informative model(s).

**Week 5–6: Borzoi and AlphaGenome scoring**
- [ ] E5: Score all PRS SNPs with Borzoi and/or AlphaGenome
- [ ] E7: Perform distance-stratified analysis (Hypothesis 6) — where does each model add value?
- [ ] E16: ISM-based fine-mapping at PARM loci — identify the predicted causal variant in each LD block
- **Deliverables**: Multi-model score table for all PRS SNPs. Analysis of where PARM vs. Borzoi/AlphaGenome excel.
- **Compute**: ~40 GPU-hours for Borzoi; AlphaGenome via API (time depends on rate limits)

**Week 7–8: Multi-model integration and eQTL validation**
- [ ] E6: Multi-model concordance analysis (Hypothesis 2) — cross-reference with GTEx eQTL fine-mapping
- [ ] E20: TF motif annotation of top predicted functional variants using PARM RS identification
- [ ] E17: Validate against published MPRA data at cancer risk loci (search for and download available data)
- **Deliverables**: Multi-model concordance matrix. TF motif disruption annotations. MPRA validation results.
- **Person-hours**: ~80 hours
- **Go/no-go decision**: If multi-model concordance does NOT correlate with eQTL PIP, the multi-model strategy may not add value beyond any single model. Simplify subsequent analyses.

---

### Month 3: Combinatorial Analysis (Core Novelty)

**Objective**: Test for non-additive effects and generate predicted haplotype-level expression effects.

**Week 9–10: Within-window combinatorial analysis with PARM**
- [ ] E8: Run PARM combinatorial mutagenesis — all pairs and top triples of predicted functional variants within each 600 bp window
- [ ] E9: Quantify non-additivity (Hypothesis 3) — compute interaction scores for all pairs
- [ ] Identify the top predicted "synergistic" pairs and triples per locus
- **Deliverables**: Interaction score matrix for all variant pairs. Classification of additive vs. non-additive loci.
- **Compute**: ~20 GPU-hours for PARM combinatorial analysis

**Week 11–12: Long-range haplotype scoring with Borzoi/AlphaGenome**
- [ ] E10: Score top candidate haplotypes (from PARM combinatorial + known PRS SNP combinations) with Borzoi/AlphaGenome
- [ ] Generate the predicted expression distribution for each target gene across all candidate haplotypes
- [ ] Compare PARM-only predictions (additive sum of single effects) with Borzoi full-haplotype predictions to assess whether non-additive effects persist at longer range
- **Deliverables**: Predicted expression scores for all candidate haplotypes. Assessment of whether combinatorial effects are real or artefacts of PARM's limited window.
- **Compute**: ~80 GPU-hours for Borzoi
- **Go/no-go decision**: If non-additive effects are negligible (Hypothesis 3 fails), the combinatorial approach can be simplified to additive scoring of individual variants. This still leaves the haplotype-level population analysis (Months 4–5) as viable.

---

### Month 4: Population-Level Haplotype Analysis

**Objective**: Map predictions to real human populations and test for haplotype-level disease associations and selection signals.

**Week 13–14: Extract and score observed haplotypes**
- [ ] E11: Extract observed phased haplotypes at target loci from 1000 Genomes and (if available) UK Biobank
- [ ] E12: Score all observed haplotypes with the best-performing model from Month 2 analysis
- [ ] Generate the key visualization: distribution of predicted expression for observed haplotypes (weighted by frequency) vs. theoretically possible haplotypes vs. PARM-predicted "worst-case" haplotypes
- **Deliverables**: Scored haplotype database. Key distribution plots.

**Week 15–16: Selection and disease association analyses**
- [ ] E13: Compare observed vs. expected haplotype frequencies (Hypothesis 4) — test for depletion of extreme haplotypes
- [ ] E14: If UK Biobank access is available, test haplotype-disease association (Analysis 6b)
- [ ] E15: Run iHS/nSL analysis at target loci to detect selection signals
- [ ] E18: Cross-ancestry comparison — do the same predicted-extreme haplotypes exist at different frequencies across populations?
- **Deliverables**: Statistical test results for selection signals. Disease association results (if UK Biobank data available).
- **Person-hours**: ~100 hours
- **Compute**: ~20 GPU-hours for haplotype scoring; population genetics analyses are CPU-bound
- **Go/no-go decision**: If selection signals are absent (expected to be difficult to detect for cancer variants), focus the narrative on the validation and combinatorial novelty rather than selection. If UK Biobank data is not accessible, use 1000 Genomes haplotype analysis without disease association testing.

---

### Month 5: Synthesis, Validation, and Manuscript Preparation

**Objective**: Synthesize all results, perform final validation analyses, and prepare the manuscript.

**Week 17–18: Final validation and sensitivity analyses**
- [ ] Sensitivity analysis: How do results change with different parameter choices (window size, top-K threshold, interaction score cutoff)?
- [ ] Permutation tests for all key results
- [ ] Compare PARM ISM predictions at TERT promoter (known ground truth) as a showcase example linking to the van Lieshout et al. results
- [ ] Compile a catalogue of all loci with strong predicted non-additive effects, annotated with TF motifs and biological interpretation

**Week 19–20: Manuscript preparation**
- [ ] Write results around 3 main figures: (1) Single-SNP validation (PRS vs. controls, model comparison), (2) Combinatorial/haplotype analysis (non-additive effects, predicted haplotype landscapes), (3) Population-level results (observed vs. predicted haplotype distributions, selection signals)
- [ ] Prepare supplementary materials with complete score tables for all PRS SNPs across all models
- [ ] Draft a discussion section addressing: limitations, comparison with existing methods, implications for PRS development, and future directions
- **Deliverables**: Complete manuscript draft. Supplementary data tables. Code repository for reproducibility.

---

### Contingency Plans

**If PARM fails to discriminate PRS vs. control SNPs (Month 1 go/no-go fails)**:
- Pivot to using AlphaGenome as the primary model for all analyses
- The project becomes: "Systematic evaluation of AlphaGenome for cancer PRS variant interpretation" — still novel and publishable
- Alternatively, investigate *why* PARM fails — this may reveal that most PRS SNPs act through distal enhancers (itself a finding)

**If combinatorial effects are negligible (Month 3 go/no-go fails)**:
- Focus the paper on single-SNP model comparison and ISM-based fine-mapping (E16)
- The ISM-based fine-mapping of PRS loci is independently valuable and publishable

**If UK Biobank access is not obtained in time**:
- Use 1000 Genomes for haplotype analysis (no disease association, but haplotype frequency and selection analyses are still possible)
- Consider FinnGen or Biobank Japan as alternatives

**If AlphaGenome API has restrictive rate limits**:
- Use Borzoi as the long-range model (code/weights are available for local running)
- Accept slower computation but full control

---

### Resource Requirements Summary

| Resource | Quantity | Estimated Cost |
|----------|----------|---------------|
| GPU compute (A100 or equivalent) | ~180 GPU-hours total | ~$500–$900 (cloud) or free (institutional) |
| Storage | ~500 GB for model weights + data | ~$25/month (cloud) |
| Data access (UK Biobank) | Application + approval | Free (academic) but 2–6 month wait |
| Data access (1000 Genomes, GTEx, gnomAD) | Download | Free, immediate |
| Data access (AlphaGenome API) | Registration | Free (non-commercial), immediate |
| Personnel | 1 postdoc/PhD student full-time, 1 PI 20% time | — |

---

### One-Page Executive Summary

**Title**: *Sequence-Based Deep Learning Models Predict Biologically Meaningful Effects at Cancer Risk Loci: From Single Variants to Haplotype Landscapes*

**The problem**: Polygenic risk scores for cancer aggregate hundreds of common genetic variants, most of which are non-coding and of unknown function. Current approaches treat these variants as independent, additive risk factors. We lack (1) systematic evidence that sequence-based deep learning models can prioritize disease-relevant regulatory variants, (2) any understanding of combinatorial (haplotype-level) effects of co-occurring risk variants on gene expression, and (3) evidence for whether natural selection acts on regulatory haplotypes at cancer loci.

**What we will do**: We will use three complementary sequence-based models — PARM (lightweight, MPRA-trained, promoter-focused), Borzoi (long-range, RNA-seq-trained), and AlphaGenome (multimodal, 1 Mb context) — to systematically score all variants in the PRS313 (breast cancer), GRS451 (prostate cancer), and PRS-5/PRS-combined (HCC) polygenic risk scores. We will validate that PRS-included variants have larger predicted regulatory effects than matched controls, identify cases where multiple variants interact non-additively, score real haplotypes from population data, and test whether the most extreme predicted haplotypes are depleted by purifying selection.

**The most important expected finding**: We anticipate showing that a two-stage approach (fast local PARM scan + long-range Borzoi/AlphaGenome validation) can identify the likely causal variant at PRS loci better than any single model alone, and that haplotype-level predictions reveal non-additive regulatory effects invisible to standard single-SNP GWAS analysis. The secondary finding — that predicted-extreme haplotypes are underrepresented in healthy populations — would, if confirmed, provide the first population-genetic evidence for selection on regulatory haplotype structure at cancer risk loci.

**Why it matters**: This work would establish a framework for using the latest generation of sequence-based genomic models as tools for precision oncogenetics — moving from statistical associations to mechanistic predictions of how and why specific non-coding variants alter cancer risk. It directly addresses the "variant interpretation bottleneck" that limits the clinical translation of polygenic risk scores.

---

## APPENDIX: SEARCH QUERIES TO EXECUTE

Execute web searches for the following and integrate the results into the relevant sections:

1. "PARM promoter activity regulatory model cancer risk variants 2025 2026" — any applications of PARM to germline disease variants
2. "Borzoi sequence model cancer GWAS variant effect prediction" — Borzoi applied to cancer genetics
3. "AlphaGenome cancer risk variant scoring PRS" — AlphaGenome for cancer risk interpretation
4. "Flashzoi Borzoi distilled model" — clarify what Flashzoi is and whether it's published
5. "sequence-based model haplotype combinatorial variant effect prediction" — has anyone done this?
6. "MPRA breast cancer risk loci allelic effects" — experimental data for validation
7. "MPRA prostate cancer 8q24 regulatory variants" — experimental data at key prostate cancer locus
8. "fine-mapped causal variants breast cancer GWAS Fachal 2020" — fine-mapped variant lists
9. "fine-mapped prostate cancer GWAS causal variants Wang 2023" — fine-mapped variant lists
10. "PRS313 breast cancer SNP list coordinates" — exact variant positions for PRS313
11. "GRS451 prostate cancer variant list supplementary" — exact variant positions for GRS451
12. "polygenic risk score variant effect prediction deep learning" — general field review
13. "Enformer eQTL cancer risk loci prediction" — Enformer applied to cancer eQTLs
14. "purifying selection regulatory haplotypes human promoters" — selection on regulatory variation
15. "non-additive epistatic effects non-coding regulatory variants" — regulatory epistasis
16. "PolyFun functionally informed fine-mapping sequence model scores" — combining models with fine-mapping
17. "allele-specific expression cancer risk loci GTEx" — ASE as validation data
18. "UK Biobank whole genome sequencing phased haplotypes cancer 2025 2026" — latest UK Biobank WGS for cancer
19. "ExPecto DeepSEA variant effect cancer risk benchmark" — earlier model benchmarks for comparison
20. "Vaishnav yeast promoter combinatorial mutations deep learning" — combinatorial variant effect precedent
21. "ENCODE cCREs cancer cell types breast prostate liver" — regulatory element annotations
22. "iHS nSL selection scan cancer risk loci regulatory variants" — selection scans at cancer GWAS loci
23. "Karollus promoter enhancer prediction accuracy sequence models 2023" — PARM vs distal enhancer prediction
24. "Tewhey MPRA haplotype multiple variants allelic effects" — multi-variant MPRA experiments
25. "SNPsnap matched control variants generation tool" — tool for generating matched controls

---

## CRITICAL REMINDERS

- **Do not be superficial.** For each model, provide enough detail that a researcher could run it. For each experiment, specify exact data sources, file formats, and statistical tests.
- **Always provide specific paper citations** with year and first author. Where possible, provide DOIs.
- **For the cancer-specific analyses, be concrete**: refer to specific PRS model names (PRS313, GRS451, PRS-5), specific PARM cell-type models (MCF7, LNCaP, HepG2), specific gene names at risk loci, and specific rs-numbers where possible.
- **Reason about what is feasible in five months**: A single researcher with GPU access can accomplish a lot with PARM (it's fast), but Borzoi/AlphaGenome scoring at scale requires planning. Be realistic about what can be accomplished when.
- **The biology matters**: The ultimate test of this project is whether model predictions correspond to known cancer biology. Every analysis should connect back to biological interpretation: Which TF motifs are disrupted? Which genes are affected? Does the direction match oncogene/TSG biology?
- **Address the "so what" question**: Even if models predict effects at PRS loci, what does this *add* beyond knowing the SNP is in the PRS? The answer must be: (1) mechanism (how the variant affects expression), (2) prioritization (which of the tag SNPs is causal), (3) combinatorics (haplotype-level effects invisible to standard GWAS), and (4) counterfactual reasoning (what haplotypes *could* exist but don't).
- **Search the web aggressively** for the latest papers and results. This field (sequence-based genomic models) moved from Enformer → Borzoi → AlphaGenome in the span of 3 years (2021–2026). There may be papers published in 2025–2026 that are directly relevant and not in the provided materials.
- **Be honest about limitations**: PARM is a reductionist promoter model that misses enhancers and 3D genome effects. Borzoi/AlphaGenome have better resolution but are trained on correlative data. Neither model has been validated for multi-variant haplotype predictions. The selection signal may be undetectable. State these limitations clearly and propose mitigations.
