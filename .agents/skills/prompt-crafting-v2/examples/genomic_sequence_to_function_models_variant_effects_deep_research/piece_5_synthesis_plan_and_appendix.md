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
