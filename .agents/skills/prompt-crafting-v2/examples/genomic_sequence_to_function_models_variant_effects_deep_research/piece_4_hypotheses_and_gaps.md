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
