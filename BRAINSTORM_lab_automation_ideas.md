<div align="center">
  <img src="images/brainstorm_ridder_lab.png" alt="Brainstorm de Ridder Lab" width="800">
</div>

# Introduction and setup

The goal of this document is to catalogue ideas for lab automation tools that the de Ridder lab could use to enhance
parts of the day-to-day tasks of scientists. Specifically, using agentic search or tooling to help us contextualize papers,
deal with the flood of e-mail, get automatic (augmented) meeting/brainstorm recordings (using local models), etc.

We will use these ideas to:
* Get cracking with making some tools at the de Ridder lab 2026 retreat hackathon
* Get at least 3 minimum viable products (MVPs) at the follow up automation/AI tooling meeting on 03-07-2026

## Hackathon instructions

The hackathon will be preceded by some tips and tricks for common use cases (deep research and agentic coding) and a public brainstorming session where we try to come up with more ideas than the initial seed ideas we thought up and collected from your input in the lab meeting on sthe 24th of April. One of the organisers (Franka, Myrthe, Adrien, Dieter) will live-edit this document to add your ideas. Then, your team takes one of the ideas and in 50 minutes tries to:

1. Create a clear design document/specification: what problem does the tool solve. What, exactly, should the tool do, and how? Save this as a .md file in a folder for your team locally. Copy and fill in [TEMPLATE.md](./submissions/TEMPLATE.md).
2. Make a first implementation of the bot/tool, as far as you get.

When the 50 minutes are up, push whatever you have made to the remote repo so you can develop it further later, and discuss what you found!

We will focus on several use cases:
1. Tools that interact with Slack, whose backend could be local or in a cloud VM. For instance: an LLM-based workflow that summarizes a paper posted on fyi-papers and pulls in related papers + comments from Bluesky. 
2. Tools that interact with code, whose backend could be the hpc. For instance: a scheduled ollama job on the hpc that takes code you have written during the day and does a (fully local) code review for, say: i) possible mistakes; ii) suggesting packages that might help in doing what you want to do; iii) surfacing code optimization possibilities using tools like [numba](https://numba.pydata.org/) or [Cython](https://cython.org/) or parallelizing with [joblib](https://joblib.readthedocs.io/en/stable/) or vectorizing with Numpy, etc.
3. Tools that just run on our laptops. For instance, a local deep research variant that uses your literature database and local models and open-source search, so that we are not beholden to cloud providers. 

Many of these overlap. The core security concern is: anything that gets exposed to the open web, even if via curated APIs (like the Arxiv paper server) is potentially dangerous and needs to be vetted: it should hence not be run on the hpc. 

# Lab automation ideas 

Ideas are numbered, the section below (optionally) has per-idea
execution ideas. 


1. Personal reading digest: based on papers you've liked on the fyi paper channel, or a source set of papers, or a selection from a lab-maintained (and editable) list of authors or the type of code you have been committing (the Big Claude is Watching You-approach)... get a personalized (weekly) reading list. Similar to tools like https://www.scholar-inbox.com/digest or https://www.semanticscholar.org/. 

2. Automatic meeting transcription, summarization, and (optionally) enrichment: an idea similar to [idea number one here](https://www.lesswrong.com/posts/bxdwSZYxKmPBres6w/10-non-boring-ways-i-ve-used-ai-in-the-last-month). Meetings are automatically recorded + transcribed. Then, this transcription is sent to an LLM for some basic fact-checking/error correction (perhaps using any powerpoint files from the meeting). From here, the sky is the limit: have the LLM look up what was discussed in earlier meetings and cross-reference it/note disagreements, list 5 must-read papers based on a web search, do a whole adversarial review (why brainstorm ideas could or could not work, suggested tools, etc.), surface important approaches that were not mentioned but could be useful, summarize this document for the next meeting, etc. [./additional_information_and_resources/Teams_transcript_example](./additional_information_and_resources/Teams_transcript_example) has an example Teams meeting transcript if you want to go that way. 

3. Powerpoint --> markdown summary bot: a bot that allows you to upload powerpoint files (active in the labmeeting and SIG Slack channels) and automatically generates a markdown summary of the contents. The summary could just be based on the contents of the slides, but you can go wild: plug in vision-LLMs or embedding models to make the graphs/visuals useful context as well, make a complete topic onboarding section (the 1,000-word context that a scientist needs to understand the concepts and problem description of the presentation), what references are cited + a summary of their contents and DOI links, etc.

4. LLM-based (local, IP-safe) grant application, paper, and/or code review: send any document and get a clear review with actionable insights. One that you can then chat further with and ask questions. You can take inspiration from [the source Cristian shared in soSOearlier](https://github.com/isitcredible/reviewer2) and more involved ideas/existing implementations from the [companion guide](/hpc/compgen/projects/lab_ai_automation/hackathon/additional_information/additional_starting_sources_local_reviewer_pipeline.md). 

5. A SIG newsletter that the entire lab receives on Slack: the SIGs are pretty siloed and since we are a large lab, group meeting presentations are few and far between. Busy postdocs, especially, have no way of knowing what is going on with everyone's project for months at a time. What if we could instead have an automatic SIG summary, based on a meeting recording (transcript), or slides, or both. Has elements of idea 2 and 3 above. Could also double as a recap of who discussed what last time. 

6. Automated sbatch/srun profiling and (lab-wide) reporting: we usually only profile jobs that are very compute-intensive, and otherwise hopefully follow the sbatch templates with a high nice-factor that Roy gave us. However: we probably overprovision or overuse both `sbatch` and `srun` jobs, and the current infrastructure requires that everyone check their own jobs' actual usage versus what was requested. Can we use automated tools to surface a daily/weekly report to members on how their jobs did and give recommendations on what to change? 

7. Automated code optimization: running local LLM code reviewers against committed/user-selected code overnight on the HPC, and get a full report of possible wall-clock speed, memory usage, etc. Could be a single pass with an LLM, or something more involved like an autoresearch-type agent (see [here](https://github.com/karpathy/autoresearch) and [here](https://github.com/huggingface/ml-intern/tree/main) and [here](https://blog.skypilot.co/research-driven-agents/)) that does profiling and autonomously tries some speed-ups and gives you a report of what worked in the morning so you can choose what to merge. 

8. Generating interactive demos/paper websites for papers (or datasets): coding agents can do a lot, but are still fickle and 'dumb' in important ways. But what they excel at are tasks that fall into the bucket 'what if you had an army of junior coding interns that never sleep and they could do anything?'. Good-enough frontend/UI design especially, is something they excel at. 

Automated sbatch profiling and reporting
Reviewing our own papers (using local agents, IP safe)
Generating interactive demos/paper website for papers (or datasets)
Journal Club preparation

# Implementation ideas

1. lalal

2. [This model](https://github.com/microsoft/VibeVoice/blob/main/docs/vibevoice-asr.md) does realtime transcription on up to 60 minutes of audio, including speaker detection and attribution. It can be run using the [huggingface transformers library](https://huggingface.co/microsoft/VibeVoice-ASR-HF). However, running a bot in Teams is not so easy. Maybe the easiest is just using the Teams transcription feature.

