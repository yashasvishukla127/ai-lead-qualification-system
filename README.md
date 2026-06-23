---
title: AI Lead Qualification System
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# AI Lead Qualification System




# AI Lead Qualification System

> Production-style lead analysis and email drafting pipeline — built as Project 1 
> of a 15-project roadmap transitioning from backend Java engineering into 
> agentic AI development.

**Status:** Core pipeline complete and tested locally. Deployment to Railway in progress.

🔗 Live : https://ai-lead-qualification-system.up.railway.app/

# Cost Dashbaord
https://ai-lead-qualification-system.up.railway.app/api/v1/dashboard

## What it does

Takes raw lead text → analyses intent/urgency via LLM → drafts a personalised 
email → self-reviews and refines if tone score is weak → generates 3 follow-up 
emails with distinct angles (value-add, urgency, final check-in).

## Architecture
 

## Key engineering decisions

- **Pydantic v2 for structured LLM output** — LLMs don't reliably return clean 
  JSON. Strict schemas with Literal types fail loudly at the boundary instead 
  of letting bad data flow downstream.
- **Temperature 0 for analysis, 0.6 for drafting** — deterministic scoring, 
  natural variation in email tone.
- **Self-review loop** — emails below tone_score 7 get one automatic refine pass.
- **Correlation IDs on every request** — traceable logs across concurrent requests.
- **Per-call cost tracking → daily aggregated dashboard** — cost broken down 
  by model and token type, not just a running total.

## Failure modes encountered

- Cost logging initially failed silently — ran with zero errors, csv stayed 
  empty. No crash signal at all.
- Railway's stateless containers reset local file storage on restart — 
  fixed with a persistent volume-backed data directory.

## What I'd do differently

- Add the cost dashboard from day one instead of bolting it on after.
- Write the Pydantic schema before the prompt, not after.

## Stack

FastAPI · Pydantic v2 · Anthropic Claude API · pytest · Railway

 










-------------------------------------------------------------------------------------------------------------------------------------------------------------------










to run every thing - 
uvicorn src.main:app --reload --port 8000

**Open Swagger UI:**
http://localhost:8000/docs

**to run test**
Run tests:
pytest tests/test_api.py -v
pytest tests/test_errors.py -v
pytest tests/test_pipeline.py -v
