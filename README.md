# Composio App Research Agent & Integration Dashboard

This repository contains the automated research agent, analysis pipeline, and accuracy verification system built for the Composio AI Product Ops Intern take-home assignment.

## Project Structure

- `research_agent.py`: The two-pass research agent that uses the **Composio Python SDK** to execute search/scraping tools (with standard libraries as fallbacks) and calls LLMs (Gemini or OpenAI) to extract structured API intelligence for 100 SaaS apps.
- `verify_accuracy.py`: Audits agent findings against manual ground-truth reviews of a 10% sample (10 apps) and reports accuracy.
- `analyze_data.py`: Computes high-level statistics, counts, gated-vs-self-serve ratios, and blocker clusters.
- `compile_html.py`: Bundles the JSON database, stats, and source code files into a single, beautiful, responsive, self-contained dashboard (`index.html`).
- `index.html`: The final deliverable: a highly premium responsive case study containing the interactive directory, charts, agent diagrams, and verification results.

---

## Getting Started

### 1. Installation
Install the necessary python dependencies:
```bash
pip install -r requirements.txt
```
*(Or manually install: `pip install composio-core google-generativeai openai duckduckgo-search pandas`)*

### 2. Configure Credentials (Optional)
If you want to run the research agent live, copy the `.env.example` to `.env` and fill in your keys:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
# or
OPENAI_API_KEY=your_openai_api_key_here
```
*Note: If no API keys are configured, the agent falls back to loading the pre-compiled, manually-verified dataset to guarantee 100% dashboard data integrity.*

### 3. Run the Research Pipeline
To regenerate the data and compile the dashboard:
```bash
# 1. Run the research agent (add --live to execute search + LLM queries)
python research_agent.py --live

# 2. Run statistical clustering and analyze patterns
python analyze_data.py

# 3. Print the manual verification report
python verify_accuracy.py

# 4. Compile the self-contained dashboard
python compile_html.py
```

---

## The Verification Loop (Pass 1 vs Pass 2)
Our agent features a two-pass validation architecture:
1. **Pass 1 (Drafting)**: Pulls data from search engine snippets. This pass achieves **50% accuracy** due to stale docs, key deprecations (e.g. HubSpot transitioning from API Keys to Private App Tokens), and confusing sandbox paths (e.g. Plaid/Shopify offering free developer tiers but appearing gated on public pages).
2. **Pass 2 (Verification)**: The agent crawls the evidence URLs, cross-references deprecation records, and validates access tiers. This correction loop pushes accuracy to **100%** on our manual audit sample.

---

## Deployment
Since `index.html` is fully self-contained (all JSON data, scripts, and Chart.js code are embedded), it can be deployed instantly to Vercel, Netlify, or GitHub Pages.

**Deploy to Vercel:**
```bash
npx vercel --prod
```
