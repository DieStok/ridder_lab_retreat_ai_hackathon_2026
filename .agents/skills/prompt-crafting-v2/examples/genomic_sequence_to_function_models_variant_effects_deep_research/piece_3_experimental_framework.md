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
