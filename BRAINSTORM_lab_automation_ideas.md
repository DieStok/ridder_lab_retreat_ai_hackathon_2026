# Introduction and setup

The goal of this document is to catalogue ideas for lab automation tools that the de Ridder lab could use to enhance
parts of the day-to-day tasks of scientists. Specifically, using agentic search or tooling to help us contextualize papers,
deal with the flood of e-mail, get automatic (augmented) meeting/brainstorm recordings (using local models), etc. 

We will use these ideas to:
* Get cracking with making some tools at the de Ridder lab 2026 retreat hackathon
* Get at least 3 minimum viable products (MVPs) at the follow up automation/AI tooling meeting on 03-07-2026

## Hackathon instructions

The hackathon will be preceded by some tips and tricks for common use cases (deep research and agentic coding) and a public brainstorming session where we try to come up with more ideas than the initial seed ideas we thought up and collected from your input in the lab meeting on sthe 24th of April. One of the organisers (Franka, Myrthe, Adrien, Dieter) will live-edit this document to add your ideas. Then, your team takes one of the ideas and in 50 minutes tries to:

1. Create a clear design document/specification: what problem does the tool solve. What, exactly, should the tool do, and how? Save this as a .md file in a folder for your team locally.
2. A first implementation of the bot

# Lab automation ideas 

Ideas are numbered, the section below (optionally) has per-idea
execution ideas. 


1. Personal reading digest: based on papers you've liked on the fyi paper channel, or a source set of papers, or a selection from a lab-maintained (and editable) list of authors or the type of code you have been committing (the Big Claude is Watching You-approach)... get a personalized (weekly) reading list. Similar to tools like https://www.scholar-inbox.com/digest or https://www.semanticscholar.org/. 

2. Automatic meeting transcription, summarization, and (optionally) enrichment: an idea similar to [idea number one here](https://www.lesswrong.com/posts/bxdwSZYxKmPBres6w/10-non-boring-ways-i-ve-used-ai-in-the-last-month). Meetings are automatically recorded + transcribed. Then, this transcription is sent to an LLM for some basic fact-checking/error correction (perhaps using any powerpoint files from the meeting). From here, the sky is the limit: have the LLM look up what was discussed in earlier meetings and cross-reference it/note disagreements, list 5 must-read papers based on a web search, do a whole adversarial review (why brainstorm ideas could or could not work, suggested tools, etc.), surface important approaches that were not mentioned but could be useful, summarize this document for the next meeting, etc.

3. Powerpoint --> markdown summary bot: a bot that allows you to upload powerpoint files (active in the labmeeting and SIG Slack channels) and automatically generates a markdown summary of the contents. The summary could just be based on the contents of the slides, but you can go wild: plug in vision-LLMs or embedding models to make the graphs/visuals useful context as well, make a complete topic onboarding section (the 1,000-word context that a scientist needs to understand the concepts and problem description of the presentation), what references are cited + a summary of their contents and DOI links, etc.

4. LLM-based (local, IP-safe) grant application, paper, and/or code review: send any document and get a clear review with actionable insights. One that you can then chat further with and ask questions. You can take inspiration from [the source Cristian shared in soSOearlier](https://github.com/isitcredible/reviewer2) and more involved ideas/existing implementations from the [companion guide](/hpc/compgen/projects/lab_ai_automation/hackathon/additional_information/additional_starting_sources_local_reviewer_pipeline.md). 

5. A SIG newsletter that the entire lab receives on Slack: the SIGs are pretty siloed and since we are a large lab, group meeting presentations are few and far between. Busy postdocs, especially, have no way of knowing what is going on with everyone's project for months at a time. What if we could instead have an automatic SIG summary, based on a meeting recording (transcript), or slides, or both. Has elements of idea 2 and 3 above. Could also double as a recap of who discussed what last time. 

6. Automated sbatch profiling and (lab-wide) reporting: we usually only profile jobs that are very compute-intensive, and otherwise hopefully follow the sbatch templates with a high nice-factor that Roy gave us. Howe

Automated sbatch profiling and reporting
Reviewing our own papers (using local agents, IP safe)
Generating interactive demos/paper website for papers (or datasets)
Journal Club preparation

# Implementation ideas

1. lalal

2. [This model](https://github.com/microsoft/VibeVoice/blob/main/docs/vibevoice-asr.md) does realtime transcription on up to 60 minutes of audio, including speaker detection and attribution. It can be run using the [huggingface transformers library](https://huggingface.co/microsoft/VibeVoice-ASR-HF). However, running a bot in Teams is not so easy. Maybe the easiest is just using the Teams transcription feature. 