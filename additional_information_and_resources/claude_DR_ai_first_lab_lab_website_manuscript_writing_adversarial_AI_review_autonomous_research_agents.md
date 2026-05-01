# AI/LLM-Augmented Computational Lab Automation Landscape (April 2026): Outputs, Aspirations & Synthesis — Parts 6–10

*A senior research engineer's working guide for an AI-first computational lab (5–25 people; PhDs, postdocs, research engineers; HPC access; bioinformatics, ML, and computational science). Prompt B of a two-part series — covering interactive lab websites, manuscript writing with adversarial reviewer simulation, autonomous research agents, a curated first-hand reading list, and the full adoption ladder.*

---

## Preface: how to read this half of the guide

Prompt A of this series covered the "input side" of an AI-augmented lab: literature/RAG, coding agents, bureaucracy and documentation drudgery, meeting transcription, and journal clubs. Those tools earn their keep by consuming attention before research even starts. The five parts that follow are different. They sit on the **publishing and aspirational side** of the lab — what your lab puts back out into the world (a website, a manuscript) and what your lab dreams of pointing an agent at while the team sleeps (an autonomous research run).

The honest framing for April 2026: Parts 6 and 7 are fully production-ready and have been for at least a year. Part 8 — autonomous research agents — has crossed an important threshold (a Sakana paper genuinely cleared peer review at an ICLR workshop; FutureHouse's Robin produced a real ophthalmology lead in 2.5 months; Edison Scientific's Kosmos is doing things that an ordinary lab simply cannot replicate manually) but it is also where vendor marketing diverges most sharply from researcher experience. I will be specific about that gap. Part 9 is the heart of the guide for a 5–25-person lab: a real reading list of first-hand adoption posts, not a vendor matrix. Part 10 then puts Prompts A and B together into a single ordered adoption ladder.

A practical note about evidence quality. Throughout this document I distinguish *peer-reviewed Nature/ICLR-level work*, *open-source repository state*, *lab-validated experimental results*, *vendor blog claims (use with skepticism)*, and *first-hand researcher posts (highest signal for adoption decisions)*. When I cannot verify a claim after multiple searches, I say so.

---

## Part 6 — Interactive lab websites: from static brochure to grounded chatbot front door

### 6.1 What an AI-first lab actually deploys

For a small computational lab in 2026, the realistic stack for an interactive lab website is the same stack the rest of the open-source academic world has converged on, plus an optional grounded-chat layer. The dominant choices are **al-folio** (Jekyll), **academicpages** (also Jekyll), **Quarto websites**, and to a lesser extent **Hugo Blox / Hugo-Academic**. Each has the characteristic that publication, project, and people pages are generated from BibTeX + YAML rather than hand-edited HTML, which is the only sustainable substrate once you start layering AI features on top.

The most used template in computational research is `alshedivat/al-folio`, which the maintainers describe explicitly as a theme used "for homepages, blogs, lab pages, as well as webpages for courses, workshops, conferences" and which natively renders publications from `_bibliography/papers.bib` via jekyll-scholar, supports Distill-style blog posts, ships with light/dark mode, GDPR-compliant cookie consent, and Open Graph previews — all features you would otherwise duct-tape together. Real labs cited in the README include the Hay Lab (Caltech), SAILING Lab, and the UCSF Decision Lab, and the repo lists CMU PGM, CMU Deep RL, and CMU Distributed Systems among course deployments. `academicpages/academicpages.github.io` is the closest competitor at roughly 16.6k stars and 6.1k forks (per the project's GitHub releases page), distinguished mostly by being slightly more conservative and easier for non-coder PIs to operate.

For labs already using R/Python notebooks, **Quarto** has quietly become the more compelling option since 2024 because the same toolchain that produces the lab's papers and reports also produces the website. Drew Dimmery's `ddimmery.com` is the canonical demonstration: a single repo where `quarto render` builds the site, GitHub Actions handle deploys, and Quarto's "freeze" feature avoids re-rendering blog posts whose source has not changed. The Crump lab at Brooklyn College has gone further and converted both their lab site and their active research projects to Quarto, with PI Matt Crump documenting the migration in detail on `crumplab.com`. The Affective Computing Lab at the University of Kansas (`affcom.ku.edu`, source at `github.com/jmgirard/affcomlab`) is the most-cited "research lab in pure Quarto" example in the awesome-quarto list.

**My deployment recommendation for a 5–25-person AI-first lab as of April 2026:**

1. **al-folio** if you have at least one engineer comfortable in Ruby/Liquid and you want the broadest community of forks to crib from.
2. **Quarto** if your blog posts will routinely contain executable Python/R/Julia (which, for a computational lab, they should) — this is where Quarto's all-in-one story actually pays off.
3. **academicpages** if your PI wants to do edits in the GitHub web UI without ever cloning anything.
4. Avoid **Wix/Squarespace/WordPress** for a research lab. They look fine but cost you the BibTeX-to-publications-page automation, the version-controlled history, and the ability to ship a chatbot under a `/ask` path without fighting a CMS.

### 6.2 Adding an "Ask the Lab" RAG chatbot — what works, what does not

The aspirational layer on top of a static lab site is a retrieval-augmented chatbot that can answer "what does this lab work on?", "is there a protocol for X?", "has anyone in the group worked on Y?". Three patterns are now production-grade:

**Pattern A — Static-site chatbot indexed over your own corpus.** The simplest version is a self-hosted RAG over your lab's papers (PDFs), protocols (Markdown), and website content. Umberto Griffo's `umbertogriffo/rag-chatbot` is a representative reference implementation: a FastAPI + llama-cpp-python backend with a Vite/React UI, a `RecursiveCharacterTextSplitter` adapted from LangChain to chunk Markdown without taking on the LangChain dependency, and Chroma as the vector store. The repo is honest about the trade-offs ("memory bandwidth mostly determines speed; check the bandwidth gives you acceptable speed"). For a lab of 5–25 people with ~50–500 PDFs, this scales to a single workstation.

**Pattern B — n8n or Langflow-orchestrated workflow.** If your lab already runs n8n for other automations (Prompt A's documentation territory), the same instance can host an "Ask the Lab" chatbot: an HTTP trigger + a vector store (Qdrant or Weaviate are the most-cited n8n integrations) + an LLM node. n8n has a published RAG starter template and 6,000+ community-built workflow templates as of late 2025. The advantage is that the chatbot lives next to the rest of your lab's automation, not in a separate Python service.

**Pattern C — PaperQA2 as the engine.** For computational labs in particular, the most defensible choice is to use **FutureHouse's PaperQA2** (covered more in Part 8) as the actual retrieval engine and then wrap it in a thin chat UI. PaperQA2 is a Python package (`pip install paper-qa`) that does agentic RAG over scientific PDFs with citation-traversal and contextual summarization, and that — per the September 2024 paper from Skarlinski et al. — exceeds PhD-level researchers on LitQA2 and reduces hallucinations dramatically compared to one-shot RAG. Andrew White's LinkedIn announcement of PaperQA2 captures the takeaway: *"This is the first example of AI agents exceeding human performance on a major portion of scientific research, and will be a game-changer for the way humans interact with the scientific literature."* If your lab already produces a lot of internal PDFs (papers, theses, internal reviews), PaperQA2 is the engine that already understands them.

### 6.3 First-hand adoption posts (Part 6)

- **Drew Dimmery — `ddimmery.com/posts/quarto-website/`** (Bluesky: search-tractable presence; the post itself is the canonical write-up). Quote: *"Setting up Actions means that simple updates to pages (or YAML files) can actually be done directly in the GitHub editing UI, which further lowers the barrier for my future self."* Drew's piece is the single best argument for Quarto-as-a-lab-website because it is honest about why his previous Hugo-Academic site lapsed (he could not remember the CLI to add a publication) and shows how to drive everything from `papers.bib` plus a few `.yml` files.
- **Marvin Schmitt — `marvin-schmitt.com/blog/website-tutorial-quarto/`**. Quote: *"You do not have to start the project of creating your own personal website from scratch because I have crafted a template for you."* Schmitt's tutorial is the de-facto "first lab website I ever set up" walkthrough and explicitly addresses the `.nojekyll` workaround for GitHub Pages serving Quarto-rendered HTML, which is the number-one footgun for new adopters.
- **Matt Crump — `crumplab.com/blog/post_886_10_14_22_quartoProjects/`**. Quote: *"This week, just before I decided to redo my lab website in quarto, I also tried using quarto for a research project instead of vertical, and that's what really sold me."* This is the rare post that adopts the tool for the lab website *and* for active research notebooks at the same time, which is the realistic adoption path.
- **ab604 — `ab604.uk/how`**. Quote: *"For my homepage I went with an about page with hero heading using the solana template … I also wanted a dark and light theme, so I have one scss file for each."* The post documents the migration *from* Hugo Academic *to* Quarto, including the Bluesky-icon iconify shortcode. Useful precisely because it tells you what to change rather than what to choose.

For the chatbot-on-the-lab-site layer specifically, *no first-hand adoption post by a senior researcher describing a deployed "Ask the Lab" chatbot has been located after multiple searches as of April 2026*. The literature is dominated by vendor tutorials (n8n, Botpress, Stackai) and undergraduate "I built a personal RAG chatbot" Medium posts. This is a real gap: the technology stack is mature, but lab-level deployment lags. The best adoption proxy is FutureHouse's own statement that researchers integrate Crow/PaperQA "into a lab's LIMS to answer ad-hoc technical questions on demand" — but that is a vendor description, not a researcher diary.

### 6.4 What to actually deploy (decision)

For a new lab page in 2026, ship al-folio or Quarto, drop a `papers.bib`, configure GitHub Actions for autobuild on push, and *do not* ship a chatbot in the first six months. Once your `bib` and protocol library is in good shape, run PaperQA2 against it locally for the team's own use, and only expose a public chatbot if (a) you have a clear set of expected questions (e.g., "is there a protocol for ATAC-seq in this lab"), (b) you are comfortable with the answer surface, and (c) you have at least one engineer who will own its eval. The order matters: most labs that try to launch an "Ask the Lab" chatbot before they have a well-organized internal PaperQA2 fail because the underlying corpus is too sparse to ground answers.

---

## Part 7 — Manuscript writing with LaTeX-aware AI and adversarial reviewer simulation

### 7.1 The two layers, distinguished

A 2026 manuscript pipeline has two distinct AI layers, and conflating them is the most common failure mode I see in labs.

**Layer 1 — AI-aware LaTeX authoring.** This is the keystroke-level layer: Overleaf's AI Assist (released June 2025) and Digital Science's December 2025 closed-beta for an Overleaf-native multi-agent assistant; Paperpal for Overleaf (a Chrome extension that injects grammar/style suggestions without altering LaTeX source); Underleaf and PaperDebugger for image-to-LaTeX, equation generation, and inline citation review. Per Digital Science, the new Overleaf assistant will identify where citations may be missing and "with a single click, authors can add both the in-text citation and the correct bibliography entry," which is the first non-trivial agentic functionality in a mainstream LaTeX editor. The *Overleaf Labs* program is the entry path for testing it.

**Layer 2 — Adversarial reviewer simulation.** This is the manuscript-level layer: you submit a draft to one or more LLM-driven reviewer agents and get a peer review back before submitting to a journal. This is the genuinely new capability of 2025, and it is where an AI-first lab gets the biggest aspirational lift. The key academic systems are:

- **OpenReviewer / Llama-OpenReviewer-8B** (Idahl & Ahmadi, NAACL Demo 2025), an open-source 8B model specifically trained to generate ICLR/NeurIPS-style critical reviews, available at `github.com/maxidl/openreviewer`. The authors are explicit that their goal is *pre-submission feedback* for authors, not replacement of human review.
- **Reviewer2** (Gao, Singh, Joachims, arXiv:2402.10886), Cornell, which models the *distribution of aspects* a reviewer might cover and produces noticeably more detailed reviews than naive prompting.
- **AgentReview** (Jin et al., arXiv:2406.12708, EMNLP), a multi-round simulation of the entire peer review process — reviewer assessment, author rebuttal, reviewer update, AC meta-review — released as an open framework, with a 53,800-review dataset.
- **Multimodal Peer Review Simulation with Actionable To-Do Recommendations** (arXiv:2511.10902), the most recent (November 2025) system, which adds a vision–language model to ingest figures and tables and emits explicit revision to-do items aligned with a target venue.
- **Stanford Agentic Reviewer (`paperreview.ai`)**, which decomposes scoring into seven dimensions (originality, importance, claim support, soundness, clarity, value, prior-work contextualization) and then uses linear regression trained on 150 ICLR 2025 reviews to combine them. Per their tech overview, the Spearman correlation between two human reviewers on the held-out ICLR 2025 sample was 0.41; the AI-vs-human correlation was 0.42 — i.e., the AI reviewer's agreement with one human is statistically indistinguishable from another human's.
- **LLM-REVal** (arXiv:2510.12367, October 2025) is the necessary skeptic. Through multi-round simulation it shows that LLM reviewers *systematically inflate scores for LLM-authored papers* and *underrate human-authored papers that contain critical statements about risk or fairness*.

### 7.2 What this looks like in practice for a lab

The realistic 2026 workflow for an AI-first lab submitting to NeurIPS/ICLR/Bioinformatics:

1. **Draft in Overleaf with AI Assist** for grammar, equation generation, and LaTeX error fixes. Cost: ~free for limited daily quota; AI Assist is an optional add-on at the user level.
2. **Run a structured pre-submission review pass** using Stanford's `paperreview.ai` (free tier), OpenReviewer (self-hosted on a single A100), and either GPT-5/Claude with a custom rubric. Russ Poldrack's three-part Substack series (May 2025) is the methodological gold standard here: he built `poldrack/ai-peer-review`, a Python package that runs the same paper through GPT-4o, Claude 3.7 Sonnet, Gemini 2.5 Pro, DeepSeek R1, and Llama-4 Maverick (the latter two via Together.ai), and then uses Gemini to *meta-review* the anonymized reviews. The package was generated by Claude Code for under $10 in API charges and sits at `github.com/poldrack/ai-peer-review`.
3. **Read the reviews adversarially.** This is the human step. The LLM-REVal paper shows that LLM reviewers will both inflate confidence and miss novelty assessment. Treat the AI reviews as a source of *coverage* (did I forget to discuss limitations? does my abstract match my method?) rather than a verdict.
4. **Revise, then run again.** The "critique–refine" loop popularized by the multimodal peer review paper is what produces the actual lift; one-shot AI review is mostly a literacy check.

### 7.3 Adversarial *attacks* — and why you should know about them

A subplot you cannot ignore as of 2025–2026: LLM reviewers can be manipulated. The *Paraphrasing Adversarial Attack on LLM-as-a-Reviewer* paper (arXiv:2601.06884) shows that an attacker can paraphrase abstracts to inflate review scores while preserving meaning. *Breaking the Reviewer* (Lin et al., EMNLP Findings 2025, arXiv:2506.11113) catalogues prompt-injection attacks via white-text instructions hidden in PDFs, jailbreak phrases, and adversarial appendices. Both AAAI 2025 and ICLR 2025 piloted LLM-based reviewer tools, so this attack surface is now operational. For an honest lab the implication is *not* to attack reviewers, but to (a) sanitize your own LaTeX before submission to remove anything that could be construed as injection, and (b) be aware that the public review of a paper you read may have been influenced by something that is invisible to you.

### 7.4 First-hand adoption posts (Part 7)

- **Russ Poldrack — `russpoldrack.substack.com/p/reviewing-scientific-papers-using` (Part 1)**, *Part 2* (`/reviewing-scientific-papers-with`), and *Part 3* (`/reviewing-scientific-papers-with-29f`). Stanford cognitive neuroscientist, three-part series May 2025. Quote: *"Its review was thorough and caught many of the same issues that I had noticed, with only minor discrepancies."* This is the single most useful first-hand piece on adversarial reviewer simulation in a real lab — Poldrack literally hands his Gemini-2.5 review of a real preprint to his graduate class and dissects what the model got right and wrong. Bluesky handle: not located after multiple searches; he is most active on Substack and at `poldrack.github.io`.
- **Tanishq Mathew Abraham — X/Twitter `@iScienceLuvr`**. Quote on the Kosmos/Edison release: *"Edison Scientific (a brand-new company spun out of FutureHouse) releases Kosmos … 'Our beta users estimate that Kosmos can do in one day what would take them 6 months, and we find that 79.4% of its conclusions are accurate.'"* Abraham (CEO of Sophont, formerly Stability AI Research Director) is the most-followed working medical-AI researcher who consistently posts hands-on reactions to AI-scientist releases. The relevant post is at `x.com/iScienceLuvr/status/1986023952037417109`. He also posted a critique of an evaluation paper concluding that *"AI scientists produce results without reasoning scientifically … the base model is the primary determinant of both [success and failure modes]"* (`x.com/iScienceLuvr/status/2047007791865647156`), which is the most useful counterweight to vendor enthusiasm I have found.
- **Mark Torres — `markptorres.com/ai_workflows/2025-10-16-using-alphaxiv-to-read-papers`**. Quote: *"I can understand a paper in 5–10 minutes instead of 30–45 minutes, and often with better comprehension because I'm asking targeted questions."* Torres' workflow — read the AlphaXiv-generated synopsis, then ask the chat agent specific follow-ups, then only open the PDF if the paper passes that filter — is the most efficient adversarial *reading* workflow I've seen documented, and it is symmetric with the adversarial *writing* workflow.

For Overleaf AI Assist specifically, *I was not able to locate a senior researcher's first-hand adoption post (i.e., not a vendor tutorial) describing day-to-day use as of April 2026.* The product launched June 2025; the closed beta of the agentic version launched December 2025. The first-hand reviews are still mostly in vendor channels. This is a watch-list item.

---

## Part 8 — Autonomous research agents: real outputs, real failure modes

### 8.1 What "autonomous research agent" actually means in 2026

The phrase has degraded into marketing. For an AI-first lab the operative question is: *which systems will run for hours-to-days against a real research objective and produce a verifiable artifact?* The honest answer is that there are now five to seven systems for which this is true, all of which I describe below with their actual track records. I will be explicit about evidence quality.

#### Sakana AI's AI Scientist v1 and v2

**v1** (Lu et al., arXiv:2408.06292, August 2024) was the proof-of-concept: GPT-4o or Claude 3.5 Sonnet plus a human-authored code template runs an end-to-end ML research pipeline (idea → code → experiments → paper draft → automated review). **v2** (Yamada et al., arXiv:2504.08066, April 2025) removes the template requirement, introduces an experiment-manager agent, and adds *progressive agentic tree search* coordinated by best-first tree search across multiple parallel research branches. The codebase is on GitHub at `SakanaAI/AI-Scientist-v2` with a Responsible-AI-derivative license and an explicit warning to run in a Docker container.

**The headline result:** in March 2025, three v2-generated papers were submitted (with prior IRB approval and the cooperation of ICLR leadership) to the ICLR 2025 "I Can't Believe It's Not Better" workshop. One — *Compositional Regularization: Unexpected Obstacles in Enhancing Neural Network Generalization* — received reviewer scores of 6, 7, 6 (average 6.33), above the workshop's acceptance threshold, and was withdrawn before publication per protocol. Sakana published the full submission and reviews at `github.com/SakanaAI/AI-Scientist-ICLR2025-Workshop-Experiment`. In November 2025 the *AI Scientist* line was published in Nature with new scaling results.

**The honest caveats**, which Sakana itself documents and which the Joeran Beel evaluation (arXiv:2502.14297) extends:
- ICLR workshop acceptance rates are 60–70%; main-conference rates are 20–30%. Sakana acknowledges that none of its three submissions cleared its own internal main-track bar.
- The Beel evaluation found that 42% of v1 experiments failed due to coding errors; the literature-review module misclassified well-established techniques (micro-batching for SGD) as novel; manuscripts contained hallucinated numbers, missing figures, repeated sections, and "Conclusions Here" placeholder text. Beel's overall verdict: "the quality of its manuscripts currently aligns with that of an unmotivated undergraduate student rushing to meet a deadline."
- Sakana reports that v2 has *lower* success rates than v1 on tasks where v1 had a strong template, because v2 trades reliability for breadth.

**For an AI-first lab**, AI Scientist v2 is interesting as a research target, not a daily driver. The realistic deployment is to run it once on a research question your team is already considering, treat the output as a *novelty-and-feasibility prior* (does the AI Scientist think this is a known result?), and discard the manuscript draft. Cost is non-trivial: tree search uses many parallel LLM calls.

#### FutureHouse: Crow, Falcon, Owl, Phoenix, Finch → Robin → Edison Scientific Kosmos

FutureHouse is the most-respected research lab in this space because its founders (Sam Rodriques, Andrew White) are practicing scientists who have shipped wet-lab validated results.

The architectural pieces are:
- **PaperQA / PaperQA2** — agentic RAG over scientific literature, open-source at `Future-House/paper-qa`. Per the September 2024 paper, it exceeds PhD-level researchers on LitQA2; per the recent README, the project switched to calendar versioning in December 2025.
- **The FutureHouse Platform** (May 2025) exposes four agents with bird names: *Crow* (general-purpose literature QA, via API or web), *Falcon* (deep literature reviews with access to OpenTargets), *Owl* (precedent search — "has anyone done X?"), *Phoenix* (chemistry workflow planning, descended from ChemCrow). *Finch* was added as a data-analysis agent. The Michael J. Fox Foundation for Parkinson's Research is one of the first publicly-named adopters.
- **Robin** (May 2025) chains Crow, Falcon, and Finch into a multi-agent workflow. In its landmark demonstration, Robin proposed *ripasudil* — a Rho-kinase inhibitor used for glaucoma — as a novel candidate for dry age-related macular degeneration, predicting a 7.5× increase in retinal pigment epithelium phagocytosis. A small team validated this experimentally and published a peer-reviewed paper in 2.5 months, with humans only running the wet-lab steps.
- **Kosmos** (November 2025, Edison Scientific spinout, arXiv:2511.02824) is the next-generation system. Per the technical report: a single 12-hour run reads ~1,500 papers, executes ~42,000 lines of analysis code over ~200 agent rollouts, and produces a fully cited report. Independent scientists found 79.4% of statements accurate. Beta users estimated that a single 20-cycle run accomplishes 6 months of equivalent scientist time on average; the technical report reports a roughly *linear inference-time scaling law* for value of findings up to 20 cycles. Three of the seven highlighted discoveries reproduced unpublished or post-cutoff human findings; four were novel contributions. Pricing: $200/run on the Edison Scientific platform, with .edu accounts getting starter credits.

**The honest caveats:**
- The "6 months of work" estimate comes from polling 7 beta-tester scientists, which Edison's blog post acknowledges is *intrinsically suspect*. I would treat the number as "Kosmos compresses a real research thread that would have taken a long time," not as a measured productivity multiple.
- Kosmos efficiency degrades on datasets >5GB, per `36kr.com`'s coverage.
- Both Edison's blog and the Alzforum interview note that Kosmos can chase statistically significant but scientifically irrelevant findings, and tends toward absolute-statement language. Multi-run sampling is recommended.

#### The Virtual Lab (Stanford / CZ Biohub)

Swanson, Pak, Zou et al., *Nature*, July 2025 (DOI:10.1038/s41586-025-09442-9; preprint: bioRxiv 2024.11.11.623004). The Virtual Lab is an LLM-Principal-Investigator agent that assembles a team of LLM scientist agents (chemist, biologist, computer scientist, plus a "Critic" agent that injects skepticism), with a human researcher providing high-level feedback at meetings. Applied to nanobody design for SARS-CoV-2 variants JN.1 and KP.3, the Virtual Lab proposed 92 mutant nanobody designs; 90% expressed and were soluble; two had improved binding to JN.1/KP.3 while retaining ancestral-spike binding. Code at `github.com/zou-group/virtual-lab`, defaulting to GPT-5.2.

The Virtual Lab is the cleanest published example of *AI-driven hypothesis generation that produced experimentally validated results*, and it does so with transparent multi-agent meetings. Quote from James Zou (Stanford Report): *"This is the first demonstration of autonomous AI agents really solving a challenging research problem, from start to finish."* Note the framing: *autonomous agents solving the research*, with humans doing wet-lab validation.

#### Agent Laboratory and AgentRxiv (Schmidgall et al.)

Agent Laboratory (arXiv:2501.04227, EMNLP Findings 2025) is a Johns Hopkins / AMD collaboration that runs a literature review → experimentation → report-writing pipeline. Performance is best with o1-preview as the backbone; the embedded `mle-solver` won 4 medals on MLE-bench (versus 2 for OpenHands and 2 for AIDE). Repo at `SamuelSchmidgall/AgentLaboratory`.

**AgentRxiv** is the more interesting follow-up: it lets multiple agent laboratories share their outputs through a common preprint server, enabling cumulative discovery. The reported result on MATH-500 is that agents with AgentRxiv access reach 78.2% accuracy versus a 73.4–73.8% plateau without it, by iteratively building on each other's outputs (and in one case rediscovering "Simultaneous Divergence Averaging" as a generalizable reasoning technique that transferred to GPQA, MMLU-Pro, MedQA across five LLM backbones). This is the single most interesting "agents-as-collective" result of 2025; it implies that the appropriate unit of analysis is no longer a single agent but a connected agent ecosystem.

#### Google's AI Co-Scientist

A multi-agent system on Gemini 2.0/2.5 (Towards an AI co-scientist, arXiv:2502.18864, February 2025). Specialized agents — Generation, Reflection, Ranking, Evolution, Proximity, Meta-review — run a self-play "tournament" of hypotheses. The two key external validations: at Imperial College London, the AI Co-Scientist produced in days the same hypothesis (a direct DNA-fragment passage mechanism in bacteria) that José Penadés' team had taken roughly a decade to develop; this work was published in *Cell* (2025). At Stanford, the system produced drug-repurposing candidates for AML — including KIRA6 — and three were experimentally validated to inhibit AML cell viability at clinically relevant concentrations.

In December 2025 Google DeepMind announced an accelerated-access program for all 17 US Department of Energy National Laboratories, beginning with AI Co-Scientist, as part of the White House's *Genesis Mission*.

#### MLE-bench, RE-Bench, and AIDE — the engine room

The systems above are vertical applications. Underneath them are two benchmarks and one open-source agent that an AI-first lab can run on its own HPC cluster.

**MLE-bench** (Chan et al., OpenAI, arXiv:2410.07095, ICLR 2025) is 75 Kaggle competitions with rebuilt train/test splits. As of November 2025 the leaderboard top entries are *Thesis* with gpt-5-codex (48.44 ± 3.64% on All split, 65.15% on Lite), *CAIR MLE-STAR-Pro-1.5* with Gemini-2.5-Pro (44.0%), and *FM Agent* with Gemini-2.5-Pro (43.56%). OpenAI froze the leaderboard for new submissions on April 24, 2026 pending a fairness review.

**RE-Bench** (METR, November 2024, arXiv:2411.15114) is seven hand-crafted ML R&D tasks (scaling-law experiments, GPU kernel optimization, fix-corrupted-embedding, finetune-LLM-Foundry-faster, etc.) with 71 expert human attempts (61 distinct researchers) as a baseline. The headline result that I see misquoted often: on a 2-hour budget agents *outperform* humans by ~4×; on an 8-hour budget the best human still beats the best agent by ~2× and humans continue to improve at long horizons while agents plateau. Repository at `github.com/METR/RE-Bench`.

**AIDE** (`WecoAI/aideml`, arXiv:2502.13138) is the open-source ML-engineering agent that scaffolds AI Scientist v2 itself and that achieves three times the medal rate of the next-best autonomous agent on MLE-bench. AIDE uses a tree-search over solution drafts and is the de-facto reference scaffolding in the field. Per the AIDE site, "AIDE boosts performance 3.5× over o1-preview alone on MLE-Bench Lite." For an AI-first lab, AIDE is the right starting point if you want to *roll your own* automated research agent against your own benchmarks rather than buy Kosmos credits.

### 8.2 Agents4Science: a venue specifically for this stuff

The 1st Open Conference of AI Agents for Science (`agents4science.stanford.edu`) was held virtually on October 22, 2025, chaired by James Zou (Stanford), Owen Queen, Nitya Thakkar, and Eric Sun, with submissions closing September 5, 2025. The defining rule: *AI must be the sole first author* and all reviews are AI-generated (with NeurIPS-2025-style template); a human expert advisory board makes final selection for orals and the three Outstanding Paper awards (each $10,000 in Together AI compute credits). Per the *Science News* coverage, computational astrophysicist Risa Wechsler reviewed submissions and reported that papers were "technically correct, but … neither interesting nor important," and that "the technical skill of AI can mask poor scientific judgment." Submissions, reviews, and autonomy scores are publicly available on OpenReview (`openreview.net/group?id=Agents4Science/2025/Conference`).

For an AI-first lab, Agents4Science is the appropriate place to *test an autonomous-research workflow* — it is a controlled sandbox with public review traces. It is not yet a venue you would treat as on the same footing as ICLR or NeurIPS for promotion or funding purposes.

### 8.3 First-hand adoption posts (Part 8)

- **Andrew White (FutureHouse co-founder) — Bluesky `@andrew.diffuse.one`**. His pinned-era post on the Robin discovery (`bsky.app/profile/andrew.diffuse.one/post/3lpmg27ce722v`): *"FutureHouse's goal has been to automate scientific discovery. Now we used our agents to make a genuine discovery — a potential new treatment for one kind of blindness (dAMD). We had multiple cycles of hypotheses, experiments, and data analysis."* On LinkedIn, his PaperQA2 post reads *"This is the first example of AI agents exceeding human performance on a major portion of scientific research."* White also has a long Existential Hope conversation (`existentialhope.com/podcasts/andrew-white-building-an-ai-scientist-to-automate-discovery`) where he describes the day-to-day of running FutureHouse.
- **hardmaru (David Ha, Sakana AI) — Bluesky `@hardmaru.bsky.social`** and X `@hardmaru`. His original v1 post: *"It's common for AI researchers to joke amongst themselves that 'now all we need to do is figure out how to make AI write the papers for us!' but I think we're now getting there!"* (`x.com/hardmaru/status/1823179163462738083`). The official Sakana announcement of v2 with the ICLR 2025 acceptance is at `bsky.app/profile/sakanaai.bsky.social/post/3lmbwtetikc2n`.
- **Aaron Tay — `aarontay.substack.com`** (academic librarian, Singapore Management University). The most carefully-argued series of posts on academic deep research, including *"What Academic Deep Research Is Really For"*, *"Why I Think Academic Deep Research — or at Least Deep Search — Will 'Win'"*, and the deep-dive on Ai2 Paper Finder + FutureHouse PaperQA2. Quote: *"While Undermind retains an edge in user experience and polish, the openness of Ai2 Paper Finder's processes and Futurehouse's detailed reasoning traces provide valuable insights into how these tools operate, fostering trust."* Tay has been the single most useful working reviewer of academic-AI tools through 2024–2026.
- **Tanishq Mathew Abraham — X `@iScienceLuvr`** (Sophont CEO). On AI Co-Scientist and on autonomous-research evaluations. Already cited in Part 7.
- **Sam Rodriques — interviewed in *Asimov Press* (`asimov.press/p/futurehouse`)**. Quote: *"The first thing I did when thinking of making an AI scientist — which was a little bit before ChatGPT came out in September 2022 — was to figure out what is easy for humans and which tasks are easy for AI models … We've also been surprised, like many people, by how easy the cognitive work is for these models."*

For Google AI Co-Scientist *specifically*, *no first-hand researcher adoption post (beyond the published Cell paper from Penadés' group and the Stanford KIRA6 work) has been located as of April 2026.* Access is gated to DOE National Labs and a small set of academic partners.

---

## Part 9 — A curated reading list of first-hand adoption posts

This part is the practical heart of the guide. Below is a manually curated list of *first-hand* posts from working researchers about how they actually use AI tooling in their labs, organized by topic. For each entry I give the canonical URL, a 1–2 sentence quoted takeaway, and the author's Bluesky handle alongside their primary outlet where available. I have flagged entries where I could not locate a Bluesky handle after at least three searches.

### 9.1 The autonomous-agent skeptics and adopters

**Andrew White** — `bsky.app/profile/andrew.diffuse.one`, blog at `whitead.github.io`, FutureHouse blog at `futurehouse.org/research-announcements`. White is the rare practitioner who is both a founder of an AI-scientist company and a working chemist. Quote: *"This is the first example of AI agents exceeding human performance on a major portion of scientific research."* The PaperQA2 LinkedIn thread (and the engineering blog at `futurehouse.org/research-announcements/engineering-blog-journey-to-superhuman-performance-on-scientific-tasks`) is unusual in that it lays out exactly what the team measured, with ablations.

**Sam Rodriques** — `linkedin.com/in/samrodriques`, Asimov Press interview (`asimov.press/p/futurehouse`), Decoding Bio Substack interview (`decodingbio.substack.com/p/scaling-biology-003-sam-rodriques`). No active Bluesky handle located after multiple searches as of April 2026. Quote: *"People who are trusting the models without thinking may also be the same people who are trusting other people without questioning them. People need to be critical and skeptical when it makes sense to."* Rodriques is the most intellectually honest of the AI-scientist founders about the gap between what their systems do and what scientists need.

**hardmaru / David Ha** — `bsky.app/profile/hardmaru.bsky.social`, X `@hardmaru`, GitHub `hardmaru`. Sakana co-founder. Most useful for tracking the Sakana team's framing of the AI Scientist line in real time.

**Tanishq Mathew Abraham** — X `@iScienceLuvr`, blog `tanishq.ai`. CEO of Sophont, formerly Stability AI Research Director, PhD UC Davis at age 19. Most active medical-AI researcher posting hands-on reactions to AI-scientist releases. His recent thread on "AI scientists produce results without reasoning scientifically" (`x.com/iScienceLuvr/status/2047007791865647156`) is the most useful counterweight to the Edison Scientific marketing on Kosmos. *Active Bluesky handle not located after multiple searches; Abraham appears to remain primarily on X as of April 2026.*

**Russ Poldrack** — Substack `russpoldrack.substack.com`, GitHub `poldrack`. Stanford cognitive neuroscientist; the three-part series on AI peer review (cited in Part 7) is the gold-standard methodology piece. Author of *Better Code, Better Science*. Quote: *"This exercise, while qualitative and limited to a single article, convinced me that LLM review could be a useful tool to augment human peer reviewers, especially when they don't have deep expertise in the particular research domain."* *No active Bluesky handle located after multiple searches.*

**Naomi Saphra** — `nsaphra.net`, Bluesky `@nsaphra.bsky.social` (verifiable). Quote from her bsky migration guide: *"Lately, I've found bluesky suits my needs better. In spite of my similar follower counts on the different platforms, my posts are often more reshared and liked there. The discussion is more intelligent and informed, frankly, with less vapid LLM-generated engagement bait in my paper threads."* This is the canonical pointer for AI researchers who are setting up a Bluesky presence: she explicitly recommends the *Paper Skygest*, *ML Feed Blend*, and *MLSky* feeds.

### 9.2 The deep-research and academic-search reviewers

**Aaron Tay** — `aarontay.substack.com`, Singapore Management University academic librarian. Already-cited in Part 8. The one person whose posts I would tell a new lab to read end-to-end before paying for any "AI for research" subscription. Bluesky: `@aarontay.bsky.social` (verifiable).

**Ethan Mollick** — `oneusefulthing.org`, Bluesky `@emollick.bsky.social` (Mollick himself notes on his About page that he is active on X, Bluesky, and LinkedIn). Wharton professor, *Co-Intelligence* author. Strongest single posts for a lab: *Using AI Right Now: A Quick Guide* (June 2025) and *Thinking Like an AI* (October 2024). Mollick is a generalist; for science-specific use, pair him with Tay.

**Mark Torres** — `markptorres.com/ai_workflows/2025-10-16-using-alphaxiv-to-read-papers`. Quote: *"It's like having a conversation with someone who's already read and understood the entire paper."* The single most useful 1,500-word piece on how to read a paper with AlphaXiv. *No active Bluesky handle located.*

**Xiangyu Yin** — `xiangyu-yin.com/content/post_deep_research.html`. Quote: *"None of the methods can cover all references. Each deep research method has its own 'preference' in terms of papers it retrieved."* A genuinely careful red-vs-green table of which references Gemini vs OpenAI vs semi-manual deep research found for a crystal-structure-generation literature review. The closest thing to a *quantitative* lab evaluation of deep research as of late 2025.

### 9.3 The lab-website builders

**Drew Dimmery** — `ddimmery.com/posts/quarto-website/`. Already cited in Part 6. Quote: *"This means that the vast majority of posts don't need to be rendered on each build."* *No active Bluesky handle located after multiple searches.*

**Marvin Schmitt** — `marvin-schmitt.com/blog/website-tutorial-quarto/`. Already cited in Part 6. Bluesky: `@marvinschmitt.bsky.social` (verifiable).

**Matt Crump (Crump Lab)** — `crumplab.com`, Bluesky `@crumplab.bsky.social` (verifiable). Already cited in Part 6.

**`ab604` (Alistair Bailey, Southampton)** — `ab604.uk/how`. Quote: *"For my homepage I went with an about page with hero heading using the solana template."* The clearest "how to set up Quarto with Bluesky integration" walkthrough I have found. Bluesky: handle reported on the post itself (`@profile-name.bsky.social` placeholder; actual handle is in the rendered site, which I have not loaded directly).

### 9.4 The agentic-engineering pragmatists

**Simon Willison** — `simonwillison.net`, Bluesky `@simonwillison.net` (verifiable). The single most prolific working developer documenting AI-coding-agent practice in 2025–2026. His evolving definition of "agent" — *"An LLM agent runs tools in a loop to achieve a goal"* — is the most-cited working definition in the field. The *Agentic Engineering Patterns* project (`simonw.substack.com/p/agentic-engineering-patterns`) is the canonical reference for what coding-agent workflows actually look like in practice. His three-month review of November 2025 as the *inflection point when AI coding agents crossed from "mostly works" to "actually works"* is the most-cited dating of the current regime in the developer community.

### 9.5 Where adoption posts are *missing* as of April 2026

I want to be explicit about what is *not* in the literature, because absence-of-evidence here is informative:

- **No first-hand researcher adoption post for Edison Scientific Kosmos at PI-of-a-small-lab scale** has been located after multiple searches as of April 2026. The 30,000-user figure in the Alzforum coverage is a vendor claim. The closest is Betty Tijms (Amsterdam UMC) quoted in Alzforum: *"Kosmos and other agentic AI work under development makes me wonder whether we are now heading to a future where we don't read the papers we cite, and also don't write the papers of our own studies."* — which is a concern, not an adoption.
- **No first-hand researcher post on Google's AI Co-Scientist outside the published Cell/Stanford papers** has been located. Access is gated.
- **No first-hand adoption post for Sakana AI Scientist v2 in production at a non-Sakana lab** has been located. The Beel et al. evaluation paper is the closest external test, and it is critical.
- **No first-hand adoption post for an "Ask the Lab" public chatbot deployed by an academic computational lab** has been located.

These gaps are the right ones to track over the next twelve months.

---

## Part 10 — The full adoption ladder for an AI-first computational lab

This is the synthesis section: the ordered list of what an AI-first computational lab of 5–25 people actually adopts, with clear sequencing, integrating both Prompt A's tools (literature/RAG, coding agents, bureaucracy, meeting transcription, journal clubs) and the Part-6-through-Part-9 territory. I will refer to Prompt A tools by category rather than name where appropriate, since Prompt A's specific recommendations are out of my scope.

### Rung 1 — Default-on for everyone in the lab (week 1)

These are the tools where the cost-of-not-using is now higher than the cost-of-using. They are not optional in 2026.

1. **An IDE-integrated coding agent.** Cursor, Claude Code, GitHub Copilot, Codex CLI, or Gemini CLI — at least one. Per METR's July 2025 RCT (`metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/`), *early-2025* AI tools made experienced open-source developers 19% slower on their own repos. By Simon Willison's account, November 2025 was the inflection point at which this reversed. As of April 2026, an AI-first lab simply uses one. (Prompt A territory.)
2. **A literature/RAG tool that supports the lab's actual reading workflow.** AlphaXiv, FutureHouse Crow, Ai2 Paper Finder, or Undermind, depending on subfield. (Prompt A territory.)
3. **Meeting transcription with structured action-item extraction.** (Prompt A territory.)
4. **Overleaf with AI Assist**, or equivalent LaTeX editor with AI inline support, for any lab that publishes in LaTeX-heavy venues.

### Rung 2 — Project-level adoption (months 1–3)

These take real engineering effort but deliver outsized returns. Adopt them in the order given.

5. **Static lab website on al-folio or Quarto, with `papers.bib` as the single source of truth.** Build automation via GitHub Actions. Do this *before* you try to add a chatbot.
6. **PaperQA2 indexed over the lab's own PDF corpus** (papers, theses, internal reviews). Run it locally for the team. Cost is modest if you use a single A100 or batched cloud calls.
7. **A pre-submission adversarial review pass** using OpenReviewer, Stanford's `paperreview.ai`, and at minimum two additional frontier LLMs. Russ Poldrack's `poldrack/ai-peer-review` package is the right reference implementation; clone and adapt. Run it on every submission to a competitive venue.
8. **A documentation/bureaucracy automation layer.** (Prompt A territory.)
9. **A journal-club workflow that uses AlphaXiv-style synopses or PaperQA2 to pre-digest papers** before live discussion. (Prompt A territory; the AlphaXiv adoption pattern from Mark Torres' post is the cleanest version.)

### Rung 3 — Lab-strategic adoption (months 3–9)

These are the moves where AI starts shaping the *output portfolio* of the lab, not just the inputs.

10. **AIDE or a derived ML-engineering scaffold against your own internal benchmarks.** This is the right way to learn what autonomous-research agents actually do before paying for vendor systems. Run it on a problem your lab has already solved manually, and compare. Per Operand and Thesis on the MLE-bench leaderboard, this works across GPT-5, Claude, and Gemini backbones; you do not need to lock to a specific provider.
11. **A scoped Kosmos run on a real lab dataset** ($200/run on Edison Scientific, with .edu starter credits). The honest expectation: Kosmos will produce a report; ~80% of statements will be accurate; 20–30% of the directions it pursues will be statistically-significant-but-irrelevant. Treat its output as a *scoping document* for a human researcher, not a finished study.
12. **A FutureHouse Platform integration for systematic literature monitoring** — Crow on a cron schedule, scanning new papers in your lab's exact topics, integrated with your Slack/Mattermost. The Michael J. Fox Foundation use-case is the public template.
13. **Submission of a deliberately-AI-authored paper to Agents4Science 2026** as a controlled internal experiment in autonomous research. This is how you discover what your lab's actual position on AI-generated science should be, before a journal forces the decision on you.

### Rung 4 — Aspirational and watch-list (months 9+)

These are *real* technologies but their adoption surfaces are thin, vendor-controlled, or research-active. Track them but do not bet your roadmap on them.

14. **An "Ask the Lab" public chatbot.** Wait until your internal PaperQA2 deployment is mature and your Q-set is well-understood. As of April 2026, *no first-hand adoption post for this exact use case at a small academic lab has been located* — you would be in the early-adopter quartile.
15. **The Virtual Lab (Stanford) for cross-disciplinary hypothesis design.** Open-source at `zou-group/virtual-lab`, defaulting to GPT-5.2. The wet-lab nanobody validation is real; whether your lab can replicate that pattern depends on having both wet-lab access and a clear hypothesis bottleneck.
16. **AgentRxiv-style multi-lab collaboration.** The 78.2% MATH-500 result with cross-lab knowledge sharing is the most interesting collective-intelligence result of 2025; whether it transcends benchmark settings is unclear.
17. **Google AI Co-Scientist** when (and if) access opens beyond DOE National Labs and select academic partners.
18. **The next generation of Sakana AI Scientist** (post-Nature). Sakana has a credible track record of pushing the state-of-the-art; the systems they ship are still better thought of as research artifacts than as daily drivers.

### What to *avoid* explicitly

A few categories that get vendor-marketed as adoption-ready but that I would not deploy in a 5–25-person AI-first lab as of April 2026:

- **"AI lab manager" SaaS products** that promise to replace the entire lab's workflow with one tool. The differentiating reality is that the field has split into *tool* (Crow, AlphaXiv, AIDE) and *agent* (Robin, Kosmos, Virtual Lab) categories that compose differently against different workflows. A monolithic "lab AI" is a maintenance trap.
- **General-purpose chatbot wrappers** (Botpress, ChatLab, ChatBot.com) for a lab-website chatbot. They are designed for customer support, not for grounded scientific QA, and they do not handle citation traceability the way PaperQA2 does.
- **Closed-source autonomous-research tools without a published technical report.** The Sakana, FutureHouse, and Stanford Virtual Lab releases all have peer-reviewed publications and open code; that is the bar. As Naomi Saphra's bsky guide notes, the AI research community has migrated toward Bluesky in part because it is harder to make grandiose closed-source claims survive there.
- **"AI peer reviewer as a service" products** that promise to replace human review. Per LLM-REVal (October 2025), these systems systematically inflate scores for AI-authored papers and underrate human-authored papers with critical statements. Pre-submission feedback only; no review-as-verdict.

### A note on the gap between vendor narratives and researcher experience

I want to close on this because it is the through-line of Parts 6–10. The 2026 autonomous-research landscape is the first generation where the gap between *what the vendors describe* and *what working researchers experience* is large enough to matter. Sakana's Nature paper and ICLR workshop acceptance are real, but Beel's evaluation found 42% of v1 experiments fail with coding errors. Edison Scientific's Kosmos demonstrably produces 12-hour research reports with ~80% statement accuracy, but the "6 months of work" estimate comes from polling 7 beta testers. Google's AI Co-Scientist genuinely contributed to the Imperial College DNA-passage paper in *Cell*, but external researcher access is gated to a tiny fraction of the field. The Virtual Lab actually designed nanobodies that bound JN.1 and KP.3, but Stanford's James Zou is now raising ~$100M for a startup *Human Intelligence* on the back of that work, and it is not clear that the cleanest published result will generalize without that kind of resourcing.

The right working model for an AI-first computational lab in April 2026 is therefore:

- **Use the inputs side aggressively.** Coding agents, literature search, document automation, journal clubs, meeting transcription. These are the real productivity multipliers and the evidence is robust. (Prompt A territory.)
- **Use the outputs side selectively.** Lab websites: yes. Pre-submission adversarial review: yes. Kosmos-or-AI-Scientist-on-a-real-question: as a scoping experiment, once. Public "Ask the Lab" chatbot: only when you have something to ground it on.
- **Track the autonomous-research line carefully but do not stake your lab's research portfolio on it.** The headline results are impressive; the adoption surface is shallow; the failure modes are real and documented. The right posture is that of an intelligent early adopter on the second wave: read the first-hand posts in Part 9, run AIDE against your own data, submit to Agents4Science 2026 to learn the territory, and wait for the second-generation tools that will fix the failure modes the first generation has surfaced.
- **Keep your senses open.** The single best signal-to-noise filter for an AI-first lab in 2026 is the curated reading list of Part 9: Andrew White, Sam Rodriques, Tanishq Abraham, Russ Poldrack, Aaron Tay, Naomi Saphra, Ethan Mollick, Simon Willison, Drew Dimmery, Marvin Schmitt, Mark Torres, and Matt Crump. They are not a marketing channel. They are publishing what they actually do, in a form you can replicate. That is the ground truth.

If your lab's leadership reads only one external thing this quarter, it should be Andrew White's PaperQA2 LinkedIn announcement *and* the LLM-REVal paper *together*. The first tells you what is possible; the second tells you what fails when you push it. The space between those two is exactly where an AI-first computational lab in 2026 should be operating.

---

*Final note on evidence quality: throughout this document, peer-reviewed Nature and ICLR papers are cited where available; preprints are flagged as such; vendor blog posts are attributed to the vendor; first-hand researcher posts are quoted with their canonical URL. Where I could not verify a specific claim (e.g., a Bluesky handle for a specific researcher) after at least three searches, I have said so explicitly rather than fabricated a link. Readers should treat the autonomous-research benchmarks (MLE-bench, RE-Bench) as moving targets — the leaderboards have already shifted significantly between the dates the original papers were published and April 2026, and the OpenAI-frozen MLE-bench leaderboard pending fairness review is itself a signal that the benchmark community is recalibrating. The order of the adoption ladder in Part 10 will likely look different by mid-2027; the principles — input-side aggressive, output-side selective, autonomous-research as scoping rather than production — should hold.*