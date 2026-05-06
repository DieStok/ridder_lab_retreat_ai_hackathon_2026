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
