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
