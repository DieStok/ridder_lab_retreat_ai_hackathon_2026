# Deep Research Prompt: Mechanistic Interpretability, Explainable AI, and Interpreting the Sturgeon Intraoperative Brain Tumor Classifier

---

## PREAMBLE AND INSTRUCTIONS TO THE RESEARCH AGENT

You are a senior research scientist with deep expertise in mechanistic interpretability (MI), explainable AI (XAI), computational biology, and neuro-oncology genomics. You have been given an extensive set of source materials and are tasked with producing an exhaustive, technically rigorous research report followed by a concrete, prioritized six-month research plan.

**You must use web search extensively** to supplement the provided materials with the latest findings (up to your current date). Do not rely solely on the uploaded documents. For every section, actively search for the most recent papers, tools, benchmarks, and results.

**Your output must be structured as follows and must be comprehensive — target 15,000+ words across all sections combined.** Do not summarize superficially. For each technique, provide the mathematical intuition, a concrete worked example or analogy, known failure modes, and the key papers. For the Sturgeon analysis, provide specific layer numbers, parameter counts, and concrete experimental designs with expected outcomes.

---

## PART 1: COMPREHENSIVE REVIEW OF MECHANISTIC INTERPRETABILITY TECHNIQUES

### 1.1 Taxonomy and Intuitive Explanations

For each of the following MI techniques, provide: (a) an intuitive "explain like I'm a smart biologist" explanation of how it works, (b) the core mathematical formulation, (c) what it can and cannot tell you, (d) known pitfalls and failure modes with citations, and (e) the 2–3 most important papers.

**Techniques to cover (do not skip any):**

1. **Vocabulary Projection Methods**
   - Logit Lens (nostalgebraist, 2020) — projecting intermediate activations through the unembedding matrix
   - Tuned Lens (Belrose et al., 2023) — learning affine translators per layer to fix early-layer unreliability
   - Attention Lens (Sakarvadia et al., 2023) — head-specific translators
   - Backward Lens (Katz et al., 2024) — projecting gradients into vocabulary space
   - Patchscope (Ghandeharioun et al., 2024) — the unifying framework combining intervention + projection
   - Logit Spectrology (Cancedda, 2024) — SVD-based spectral filtering of the unembedding matrix

2. **Intervention-Based / Causal Methods**
   - Activation Patching (Meng et al., 2022) — noising and denoising interventions
   - Path Patching (Wang et al., 2022) — tracing importance along specific computational edges
   - Zero, Mean, and Resampling Ablation — compare reliability, OOD risks
   - Distributed Interchange Interventions (DII) and Distributed Alignment Search (DAS) (Geiger et al., 2024) — subspace-level interventions
   - Causal Scrubbing (Chan et al., 2022) — rigorous hypothesis testing
   - ACDC (Conmy et al., 2023) — automated circuit discovery
   - EAP and EAP-IG (Syed et al., 2023; Hanna et al., 2024) — gradient-approximated edge patching

3. **Sparse Autoencoders (SAEs)**
   - Standard SAE (Bricken et al., 2023) — architecture, loss function, the sparsity-reconstruction tradeoff
   - TopK SAE (Gao et al., 2024), JumpReLU SAE (Rajamanoharan et al., 2024), Gated SAE (Rajamanoharan et al., 2024a)
   - Matryoshka SAE (Bussmann et al., 2025) — hierarchical nested features
   - End-to-End SAE (Braun et al., 2024) — optimizing for functional importance via KL divergence
   - Feature splitting, feature absorption, feature composition problems (Chanin et al., 2024; Anders et al., 2024)
   - The open question: do SAE features correspond to the features the model actually uses?

4. **Probing**
   - Linear probing, sparse probing (Gurnee et al., 2023), non-linear probes
   - The correlation-vs-causation problem: probes detect feature presence, not feature usage
   - When probing is and isn't appropriate

5. **Visualization**
   - Attention pattern visualization, neuron activation visualization
   - Risks of over-interpretation and confirmation bias

### 1.2 Pitfalls and Failure Modes — A Critical Assessment

Provide a dedicated section that synthesizes the cross-cutting failure modes:

- **Out-of-distribution interventions**: When ablation pushes the model OOD, any performance drop may be artifactual (Zhang & Nanda, 2023). Discuss the specific scenarios where each ablation type fails.
- **Polysemanticity and superposition**: The linear representation hypothesis — evidence for and against. Discuss multi-dimensional features (Engels et al., 2024), circular representations, and non-linear "onion representations" (Csordás et al., 2024).
- **SAE faithfulness gap**: Reconstruction loss ≠ functional faithfulness. Discuss Gurnee (2024), Muhamed et al. (2024), and the evidence that SAEs may capture only a fraction of encoded features (Templeton et al., 2024).
- **Circuit incompleteness and sensitivity**: Circuits discovered on one dataset may not generalize to adversarial examples (uit de Bos & Garriga-Alonso, 2024). Parallel algorithms for the same task (Zhong et al., 2024).
- **Scalability**: Most MI studies use small models (GPT-2, Pythia-70M). Discuss what is known about scaling to production LLMs (Lieberum et al., 2023 on Chinchilla-70B; Templeton et al., 2024 on Claude 3 Sonnet).
- **The streetlight problem**: Most studied behaviors are simple (IOI, modular addition, greater-than). Discuss the gap between toy-task circuits and real-world model capabilities.
- **Metric selection**: Logit vs. probability vs. logit difference vs. KL divergence — when does each metric fail? (Heimersheim & Nanda, 2024; Zhang & Nanda, 2023).

---

## PART 2: LANDSCAPE ANALYSIS — LANDMARK FINDINGS AND PARADIGM PAPERS (2020–2025)

### 2.1 Timeline of Paradigm-Shifting Papers

Construct a detailed chronological timeline of the ~25–30 most important papers in MI and neural network XAI from 2020 to present. For each paper, provide: the key insight, why it was paradigm-shifting, and what it enabled downstream. **Search the web for any major papers from 2025 that may not be in the provided materials.**

Structure the timeline around these thematic arcs:
1. **The Circuits Era (2020–2022)**: Olah et al. "Zoom In" (2020) → Elhage et al. mathematical framework (2021) → Induction heads (Olsson et al., 2022) → IOI circuit (Wang et al., 2022) → Toy models of superposition (Elhage et al., 2022)
2. **The SAE Revolution (2023–2024)**: Bricken et al. monosemanticity (2023) → Scaling monosemanticity to Claude 3 Sonnet (Templeton et al., 2024) → SAE architectural improvements (TopK, JumpReLU, Gated, Matryoshka) → End-to-end SAEs
3. **The Causal Rigor Push (2022–2025)**: Causal scrubbing → DII/DAS → ACDC → EAP-IG → Benchmarking (RAVEL, MIB, CausalGym, SAEBench)
4. **Applications to Safety and Alignment (2023–2025)**: Refusal direction (Arditi et al., 2024) → Safety features in Claude (Templeton et al., 2024) → Latent space monitoring → Knowledge editing
5. **Classical XAI meeting MI**: How SHAP, LIME, integrated gradients, and attention-based explanations relate to and differ from MI approaches. Where do they overlap? Where is MI strictly superior?

### 2.2 Technique Complementarity Map

Create a detailed analysis of how different MI techniques complement each other. Specifically address:
- When should you use vocabulary projection vs. intervention vs. SAEs vs. probing?
- What is the recommended "full stack" workflow for a new interpretability investigation?
- Which technique combinations have been shown to produce more reliable results than any single technique?
- Reference the Beginner's Roadmap from Rai et al. (2024) and discuss its strengths and gaps.

### 2.3 The State of MI for Non-Transformer Architectures

Search for and discuss: What is known about applying MI techniques to:
- Simple feedforward networks (like Sturgeon)
- CNNs
- State-space models (Mamba)
- Mixture-of-experts models
- How transferable are transformer-MI insights to these architectures?

---

## PART 3: IN-DEPTH ANALYSIS OF THE STURGEON MODEL AND ARCHITECTURE

### 3.1 Architecture Deep Dive

Analyze the Sturgeon neural network in detail based on the paper (Vermeulen et al., Nature 2023):

- **Input representation**: 428,643-dimensional binary vector (−1 = unmethylated, 0 = unknown/missing, 1 = methylated). The vast majority of entries are 0 (missing) due to sparse nanopore coverage (0.5–4% of CpG sites covered at inference time).
- **Architecture**: Three fully connected layers: 428,643 → 256 (sigmoid) → 128 (sigmoid) → 91 classes. Dropout 0.5 between layers during training. Temperature-scaled softmax output.
- **Training regime**: Curriculum learning (pretrain on easy+hard, fine-tune on hard only). Adaptive sample balancing per class and sparsity level. Cross-entropy loss. AdamW optimizer. 36.8 million simulated training samples per fold.
- **Ensemble**: Four submodels from 4-fold cross-validation; final prediction uses the most confident submodel.
- **Key design choice**: The model must be robust to arbitrary missingness patterns — any subset of the 428,643 CpG sites could be observed, and the model encodes "unknown" as 0.

Discuss: What makes this architecture interpretable or not? How does the extreme sparsity of input affect what the model can learn? How does the 0-encoding of missingness interact with the learned weights?

### 3.2 What the Model Must Learn

From the biology, reason about what the model's task actually requires:

- DNA methylation patterns are cell-type and tumor-type specific. The Capper et al. (2018) classifier used random forests on 450K CpG sites and identified informative CpG subsets.
- The model must learn to classify 91 CNS tumor subtypes from extremely sparse, random subsets of methylation sites.
- Key biological question: Does the model learn tumor-type-specific methylation signatures that correspond to known biology, or does it learn statistical shortcuts?

---

## PART 4: INTERPRETABILITY PLAN OF ATTACK FOR STURGEON

### Approach A: State-of-the-Art Explainable AI Methods

For each method below, provide: (1) what it would tell us about Sturgeon, (2) exactly how to implement it, (3) expected outcomes, (4) potential pitfalls, and (5) alternative knobs to try.

#### A.1 Vocabulary Projection / Logit Lens Analogy

- Sturgeon is not a transformer, but the core idea of projecting intermediate representations to output space transfers. Describe how to:
  - Extract activations after layer 1 (256-dim) and layer 2 (128-dim)
  - Project them through the final linear layer to get class logit distributions
  - Analyze how "class certainty" evolves across layers — does layer 1 produce a rough grouping (e.g., tumor family) that layer 2 refines to subtype?
  - Compare this across different sparsity levels (10% vs 50% vs 90% of CpG sites observed)
- **Knobs**: Try with and without sigmoid activation applied before projection. Try projecting the pre-activation vs. post-activation representations.

#### A.2 Intervention-Based / Ablation Studies

- **Neuron ablation in layer 1 and layer 2**: For each of the 256 neurons in layer 1 and 128 neurons in layer 2, ablate (zero-out, mean-ablate, or noise) each neuron individually and measure the effect on classification accuracy per tumor class. Identify "class-critical neurons" and "class-suppressing neurons."
  - Hypothesis: Certain neurons will be critical for specific tumor families (e.g., neurons that activate for embryonal tumors vs. glial tumors).
  - Knobs: Compare zero ablation vs. mean ablation vs. Gaussian noise ablation. Perform combinatorial ablation of neuron pairs to detect synergies.

- **Layer-level ablation**: What happens if you freeze layer 1 and retrain only layer 2 (and vice versa)? This reveals how much each layer contributes to the classification.

- **Input group ablation**: Group CpG sites by chromosome, by genomic region (promoter, gene body, intergenic), or by CpG island status. Ablate all sites in a group and measure accuracy impact. This tests whether the model relies on distributed genome-wide patterns or concentrated regional signatures.

#### A.3 Probing Internal Representations

- **Train linear probes on layer 1 and layer 2 activations** to predict:
  - Tumor family (coarser grouping than the 91 subtypes)
  - Specific molecular markers (IDH mutation status, 1p/19q codeletion, H3K27M mutation)
  - Patient age group (pediatric vs. adult)
  - Tumor location (supratentorial, posterior fossa, brainstem, spinal)
- **Hypothesis**: Layer 1 encodes broad tumor family information; layer 2 refines to subtype-specific features. Probing accuracy should be higher for coarse labels at layer 1 and for fine labels at layer 2.
- **Knobs**: Try linear vs. 1-hidden-layer probes. If non-linear probes dramatically outperform linear ones, this suggests the representations are not linearly organized (challenging the linear representation hypothesis for this architecture).

#### A.4 Sparse Autoencoder Analysis

- **Train SAEs on the 256-dim layer 1 activations** with dictionary sizes of 512, 1024, 2048, and 4096.
- Analyze the learned SAE features: Do they correspond to interpretable biological concepts? Use automated interpretability (feed feature activation patterns to an LLM and ask it to describe what biological pattern activates the feature).
- **Key question**: In a model this small (256 → 128 neurons), is superposition even a significant issue? Or are the neurons already relatively monosemantic?
- **Knobs**: Try TopK SAE, JumpReLU SAE, and standard L1 SAE. Compare reconstruction loss vs. downstream classification accuracy when replacing original activations with SAE-reconstructed activations.

### Approach B: Classical Feature Importance Methods

#### B.1 SHAP Values (SHapley Additive exPlanations)

- **Global SHAP**: Compute SHAP values for each of the 428,643 input CpG sites across a representative set of samples per tumor class. Identify the top-100 most important CpG sites per class.
  - Implementation: Use DeepSHAP or KernelSHAP. Given the extreme input dimensionality, DeepSHAP (which leverages the network structure) is more feasible than KernelSHAP.
  - **Critical consideration**: The input is ternary (−1, 0, 1) and extremely sparse. The baseline/reference for SHAP should be the all-zeros vector (all sites unknown), which is the "no information" state. This is a natural and meaningful baseline for this model.
  - **Knobs**: Compare DeepSHAP vs. Integrated Gradients vs. gradient × input. Test sensitivity to the choice of baseline (all-zeros vs. mean-activation vs. random binary).

- **Per-class SHAP profiles**: For each of the 91 tumor classes, extract the top-100 CpG sites by SHAP magnitude. Cluster these profiles — do biologically similar tumor types share similar SHAP signatures?

#### B.2 Integrated Gradients

- Compute integrated gradients from the all-zeros baseline to each input sample.
- Advantage over SHAP: More computationally tractable for high-dimensional inputs.
- **Key analysis**: Aggregate integrated gradients across all samples of a given tumor class. The resulting "class gradient profile" shows which CpG sites, on average, drive the classification toward that class.
- **Knobs**: Vary the number of interpolation steps (50, 100, 300). Compare with SmoothGrad (adding Gaussian noise to inputs and averaging gradients).

#### B.3 Weight-Based Analysis (Direct Inspection)

- The first layer weight matrix W₁ ∈ ℝ^{428,643 × 256} directly connects each CpG site to each neuron. **Analyze this matrix directly**:
  - For each neuron j in layer 1, rank the CpG sites by |W₁[i,j]| — the absolute connection weight. The top-k sites define the "receptive field" of neuron j.
  - Cluster neurons by their weight profiles. Do clusters correspond to genomic regions? To tumor-type-relevant CpG sets?
  - **Hypothesis**: Given the extreme sparsity, the model likely learns to be a "CpG site voter" — each neuron aggregates methylation evidence from a distributed set of informative sites, and the sigmoid acts as a soft threshold.

- **Bias analysis**: The bias terms b₁ ∈ ℝ^{256} set the "default activation" of each neuron when all inputs are zero (unknown). Analyze: which neurons are active by default (positive bias) and which are suppressed? How does this interact with the temperature scaling?

#### B.4 Permutation Feature Importance

- Randomly permute each CpG site's values across samples and measure the drop in accuracy. This is model-agnostic and makes no linearity assumptions.
- **Group permutation**: Permute all CpG sites on a given chromosome simultaneously. This reveals chromosome-level importance.
- **Knobs**: Use class-specific accuracy, overall accuracy, and calibrated confidence as the performance metric. Compare individual-site vs. grouped permutation.

### Approach C: Retraining with Ablations

#### C.1 Feature Ablation via Retraining

- **Progressive CpG site removal**: Train Sturgeon from scratch, but exclude the top-k most important CpG sites (as determined by SHAP or weight magnitude). How quickly does performance degrade?
  - If performance degrades slowly: the model uses distributed, redundant information.
  - If performance degrades rapidly: the model relies on a small set of critical sites.
  - **Knobs**: Remove sites by individual importance rank, by chromosome, by CpG island status, by known biological function.

- **Restricted-input retraining**: Train models using only CpG sites from specific genomic contexts:
  - Only promoter CpG sites
  - Only gene body CpG sites
  - Only CpG islands vs. only CpG shores/shelves
  - Only sites from specific chromosomes
  - Compare the performance of these restricted models to the full model.

#### C.2 Model Architecture Ablation

- **Width ablation**: Retrain with layer 1 widths of 64, 128, 256, 512, 1024. At what width does performance plateau? This reveals the effective dimensionality of the tumor classification problem.
- **Depth ablation**: Compare 1-layer (428,643 → 91), 2-layer (428,643 → 256 → 91), and 3-layer (current) models. How much does each additional layer contribute?
- **Activation function ablation**: Replace sigmoid with ReLU, GELU, or no activation. The choice of sigmoid (which saturates) vs. ReLU (which doesn't) may significantly affect which MI techniques work.
- **Dropout ablation**: Retrain without dropout and compare the weight structure. Dropout may force the model to learn more distributed, redundant representations.

#### C.3 Output Ablation / Class Merging

- **Family-level retraining**: Merge the 91 subtypes into ~15 tumor families and retrain. Compare the weight structure of the family-level model to the subtype-level model. The differences reveal what additional information the subtype model must encode.
- **One-vs-rest retraining**: Train 91 binary classifiers (one per class). For each, identify the critical CpG sites. This gives a direct "methylation signature" per tumor type that can be compared to known biology.

### Approach D: Biology-Driven Interpretability

#### D.1 Cross-Reference with the DNA Methylation Atlas

**Search for and use the following resources:**

- **Loyfer et al. (2023), Nature**: "A DNA methylation atlas of normal human cell types" (https://www.nature.com/articles/s41586-022-05580-6). This atlas provides cell-type-specific differentially methylated regions (DMRs) across 39 human cell types, including brain cell types (neurons, oligodendrocytes, astrocytes, microglia).
- **Zhang et al. (2025), or the latest single-cell methylation atlas**: "Human Body Single-Cell Atlas of 3D Genome Organization and DNA Methylation" (https://pmc.ncbi.nlm.nih.gov/articles/PMC11974725/).

**Concrete analysis plan:**
1. Download the DMR coordinates from the methylation atlas.
2. Map these DMRs to the 450K CpG array sites used by Sturgeon.
3. For each cell type in the atlas, compute the overlap between its DMRs and the top-k Sturgeon-important CpG sites (from SHAP/weight analysis).
4. **Hypothesis**: Sturgeon-important sites for glial tumors should overlap with astrocyte/oligodendrocyte DMRs. Sites important for embryonal tumors should overlap with neural progenitor DMRs. Sites important for meningeal tumors should overlap with meningeal cell DMRs.
5. **Statistical test**: Use Fisher's exact test or a permutation test to assess whether the overlap is greater than expected by chance.

#### D.2 Cross-Reference with Known Tumor-Specific Methylation Markers

**Search for and compile a database of known methylation markers for CNS tumors:**

- **MGMT promoter methylation** (chr10): Prognostic marker for glioblastoma. Does Sturgeon weight MGMT-region CpG sites heavily for GBM classification?
- **IDH mutation-associated hypermethylation** (G-CIMP phenotype): IDH-mutant gliomas show a globally hypermethylated phenotype affecting thousands of CpG sites. Do Sturgeon's top features for IDH-mutant astrocytoma and oligodendroglioma overlap with known G-CIMP sites?
- **H3K27M mutation effects**: Diffuse midline gliomas with H3K27M show global DNA hypomethylation, particularly at H3K27me3-marked regions. Check if Sturgeon captures these patterns.
- **1p/19q codeletion-associated methylation**: Oligodendrogliomas with 1p/19q codeletion show specific methylation patterns. Do Sturgeon's important sites for the O_IDH class cluster on chromosomes 1p and 19q?
- **Medulloblastoma subgroup signatures**: WNT, SHH, Group 3, and Group 4 medulloblastomas each have distinct methylation profiles (e.g., SHH-associated PTCH1 promoter methylation). Check correspondence.
- **TERT promoter methylation**: Associated with specific glioma subtypes. Check Sturgeon's weighting of TERT-proximal CpG sites.

**For each known marker:**
1. Identify the specific 450K array probes that interrogate this region.
2. Extract Sturgeon's weight magnitudes and SHAP values for these probes.
3. Determine whether these known-important sites are among Sturgeon's top features for the relevant tumor class.
4. If they are: Sturgeon recapitulates known biology (high confidence in the model).
5. If they are not: Either (a) the model uses alternative correlated markers, or (b) the model has learned a shortcut. Investigate which.

#### D.3 Discovery of Novel Markers

- From the SHAP/weight analysis, identify CpG sites that are highly important for Sturgeon but are **not** known to be biologically significant.
- Map these sites to genes, regulatory regions, and chromatin states.
- **Hypothesis generation**: These could represent novel methylation markers for CNS tumor classification that have been missed by traditional candidate-gene approaches.
- Cross-reference with ENCODE, Roadmap Epigenomics, and the Brain Epigenome Atlas to annotate the regulatory context of these novel sites.

#### D.4 Sturgeon vs. Random Forest Feature Importance

- The original Capper et al. (2018) classifier used a random forest, which also provides feature importance scores.
- **Compare the top-k features from Capper et al.'s random forest with Sturgeon's top-k features.** How much do they overlap?
- If high overlap: Sturgeon has learned similar decision boundaries via a different architecture.
- If low overlap: Sturgeon may be exploiting different statistical structure in the data (e.g., feature interactions that random forests cannot capture, or distributed patterns across many weakly informative sites).

---

## PART 5: SPECIFIC HYPOTHESES AND EXPERIMENTAL PROTOCOLS

For each hypothesis below, provide: the hypothesis statement, the null hypothesis, the experimental protocol, the expected result if the hypothesis is true, the expected result if it is false, and what you would conclude in each case.

### Hypothesis 1: Layer 1 Learns Tumor Family Groupings; Layer 2 Refines to Subtypes
- **Protocol**: Train linear probes at both layers for family-level and subtype-level classification. Compare accuracy.
- **Expected if true**: Layer 1 probes achieve >90% family accuracy but <60% subtype accuracy. Layer 2 probes achieve >85% subtype accuracy.

### Hypothesis 2: Individual Neurons in Layer 1 Are Partially Monosemantic
- **Protocol**: For each layer-1 neuron, compute the mutual information between its activation and each tumor class label across a large test set. Identify neurons with high MI for a single class or small set of classes.
- **Expected if true**: A meaningful fraction (>20%) of neurons show high selectivity for one or a few tumor classes.

### Hypothesis 3: Sturgeon's Important CpG Sites Overlap with Cell-Type-Specific DMRs
- **Protocol**: As described in D.1. Compute overlap enrichment.
- **Expected if true**: Statistically significant enrichment (FDR < 0.05) for relevant cell types per tumor class.

### Hypothesis 4: The Model Primarily Uses ~5,000 Out of 428,643 CpG Sites
- **Protocol**: Feature ablation by retraining. Remove the bottom 90%, 95%, 99% of features by importance and retrain.
- **Expected if true**: Retraining with only the top 5% of features achieves >90% of full-model performance.

### Hypothesis 5: The "Missing" Encoding (0) Acts as an Implicit Prior
- **Protocol**: Analyze the first-layer bias terms. Compute the "default" layer-1 activation (when all inputs are 0). Feed this through the rest of the network. What class does the model predict with zero information?
- **Expected**: The default prediction should be close to the prior class distribution in the training data, or a "control tissue" class.

### Hypothesis 6: Temperature Scaling Primarily Helps with Sparse Inputs
- **Protocol**: Evaluate the model's calibration (ECE) with and without temperature scaling, stratified by input sparsity level.
- **Expected if true**: Temperature scaling provides larger calibration improvement for sparser inputs.

---

## PART 6: SYNTHESIS AGENT — PRIORITIZED SIX-MONTH RESEARCH PLAN

**You are now the Synthesis Agent.** Take all of the above research and produce a prioritized, time-bound, six-month research plan. Use the following prioritization criteria:

1. **Simplicity**: How easy is this experiment to implement? (Score 1–5, 5 = very easy)
2. **Yield**: How much insight does this experiment provide? (Score 1–5, 5 = transformative)
3. **Dependencies**: Does this experiment depend on the results of another? If so, which?
4. **Risk**: What is the probability of a useful result? (Score 1–5, 5 = near certain)

**Compute a Priority Score = (Yield × Risk) / (6 − Simplicity)** and rank all experiments.

### Format the plan as:

**Month 1–2: Foundation & Quick Wins** (highest priority score, no dependencies)
- List specific experiments with timeline
- Expected deliverables

**Month 2–3: Core Interpretability Analysis** (medium priority, depends on Month 1)
- List specific experiments
- Expected deliverables

**Month 3–4: Biological Validation** (depends on SHAP/weight results from Month 2)
- List specific experiments
- Expected deliverables

**Month 4–5: Advanced MI Techniques** (lower simplicity, higher yield)
- List specific experiments
- Expected deliverables

**Month 5–6: Synthesis, Novel Discovery, and Paper Writing**
- Synthesize all results
- Identify novel methylation markers
- Write up for publication

**For each month, specify:**
- Exact experiments to run
- Computational resources needed
- Data requirements
- Expected person-hours
- Go/no-go decision points (what would make you change the plan?)

**Finally, produce a one-page executive summary** of the entire plan with the single most important finding you expect to make, and why it matters for both the MI field and for clinical neuro-oncology.

---

## APPENDIX: ADDITIONAL SEARCH QUERIES TO EXECUTE

Execute web searches for the following and integrate the results into the relevant sections:

1. "mechanistic interpretability feedforward neural network" — what is known about MI for non-transformer FFNs?
2. "SHAP values DNA methylation classifier" — has anyone applied SHAP to methylation-based tumor classifiers?
3. "Sturgeon brain tumor classifier interpretability" — has anyone published interpretability analyses of Sturgeon?
4. "Capper DNA methylation classifier feature importance" — what CpG sites were important in the original random forest?
5. "DNA methylation atlas brain cell types CpG 450K" — for mapping atlas DMRs to the 450K array
6. "sparse autoencoder small neural network" — SAEs on non-transformer, small networks
7. "neural network interpretability medical diagnosis" — MI/XAI for clinical diagnostic models
8. "mechanistic interpretability 2025 latest papers" — what has been published in 2025?
9. "MGMT methylation 450K probe cg12434587" — specific probe IDs for known markers
10. "SAEBench MIB benchmark results 2025" — latest benchmark results for MI techniques
11. "integrated gradients binary sparse input" — specific considerations for IG with sparse binary inputs
12. "curriculum learning interpretability neural network" — does curriculum learning affect what features the model learns?

---

## CRITICAL REMINDERS

- **Do not be superficial.** For each technique, provide enough detail that a PhD student could implement it.
- **Always provide specific paper citations** with year and author.
- **For the Sturgeon plan, be concrete**: refer to specific layer dimensions (428,643 → 256 → 128 → 91), specific CpG probe IDs where possible, and specific tumor classes.
- **Reason about what is feasible**: Sturgeon is a small model. Many MI techniques designed for transformers need adaptation. Be explicit about what transfers and what doesn't.
- **The biology matters**: The ultimate test of interpretability for Sturgeon is whether the explanations correspond to known cancer biology. Always connect back to biology.
- **Search the web aggressively** for the latest papers and results. The MI field moves fast.