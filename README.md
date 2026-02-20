# AI System to Automatically Review and Summarize Research Papers
**Infosys Springboard Internship Project**

A production-ready, graph-based AI pipeline that automatically searches, downloads, analyzes, and synthesizes academic research papers into a structured literature review — powered by LangGraph, Gemini (or GPT), Semantic Scholar, and PyMuPDF.

---

## Project Structure

```
research_review/
├── app.py                  ← Gradio web UI (entry point)
├── pipeline.py             ← LangGraph graph definition & run helpers
├── state.py                ← PaperState TypedDict (shared state schema)
├── papersearch.py          ← Milestone 1: Search & download nodes
├── text_extraction.py      ← Milestone 2: Extract, normalize, section nodes
├── paper_analyzer.py       ← Milestone 3: Key findings & cross-compare nodes
├── draft_generator.py      ← Milestone 3-4: Writing, critique, revision nodes
├── utils/
│   ├── logger.py           ← Structured logger
│   └── helpers.py          ← JSON parsing, text helpers, APA formatter
├── downloads/              ← PDFs downloaded by the pipeline
├── requirements.txt
├── .env.example
└── setup.sh
```

---

## Quick Start

### Step 1: Clone / copy files
```bash
cd research_review
```

### Step 2: Automated setup
```bash
chmod +x setup.sh
./setup.sh
```

### Step 3: Configure API keys
Edit `.env`:
```dotenv
GEMINI_API_KEY=your_gemini_api_key_here
LLM_PROVIDER=gemini        # or "openai"
OPENAI_API_KEY=            # optional
SEMANTIC_SCHOLAR_API_KEY=  # optional (raises rate limit)
MAX_PAPERS=3
DOWNLOAD_DIR=downloads
```

Get your **Gemini API key** free at: https://aistudio.google.com/app/apikey

### Step 4: Run
```bash
source venv/bin/activate
python app.py
```

Open **http://localhost:7860** in your browser.

---

## Manual Installation (if setup.sh fails)

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
# Edit .env
python app.py
```

---

## Pipeline Architecture (LangGraph)

```
__start__
  │
  ├── process_input         ← Validate topic
  ├── planner               ← Generate search queries (LLM)
  ├── search_articles       ← Query Semantic Scholar API
  ├── article_decisions     ← Rank & select top papers
  ├── download_articles     ← Download open-access PDFs
  │                                        ↑ MILESTONE 1
  ├── extract_text          ← PyMuPDF text extraction
  ├── normalize_text        ← Whitespace / artifact cleanup
  ├── semantic_section      ← LLM-based sectioning
  ├── validate_sections     ← Structural validation
  ├── store_sections        ← Prepare for analysis
  │                                        ↑ MILESTONE 2
  ├── paper_analyzer        ← Extract key findings per paper
  ├── cross_compare         ← Cross-paper comparison (LLM)
  ├── write_abstract        ← 100-word abstract
  ├── write_introduction    ← Introduction section
  ├── write_methods         ← Methods comparison
  ├── write_results         ← Results synthesis
  ├── write_conclusion      ← Conclusion
  ├── write_references      ← APA 7th references
  ├── aggregate_paper       ← Assemble full draft
  │                                        ↑ MILESTONE 3
  ├── critique_paper        ← Quality review (LLM)
  ├── [conditional]────────┬── revise_paper (loop ≤2×) ─┐
  │                        └── final_draft               │
  │                              ↑ MILESTONE 4           │
  └── __end__  ←────────────────────────────────────────┘
```

---

## UI Controls

| Button | Action |
|--------|--------|
| 🔍 **Search Papers** | Search Semantic Scholar, download PDFs (Milestone 1) |
| ✍️ **Generate Draft** | Run full analysis + write all sections (Milestones 2–4) |
| 🔄 **Critique / Revise** | Re-run critique and apply one more revision pass |

---

## Output Sections

- **Abstract** — 100-word structured abstract
- **Methods Comparison** — Comparative analysis of methodologies
- **Results Synthesis** — Integrated findings across papers
- **APA References** — Properly formatted 7th edition references
- **Critique** — Quality score and revision notes
- **Final Draft** — Complete assembled literature review

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| UI | Gradio 4.x |
| Graph pipeline | LangGraph 0.2+ |
| LLM integration | LangChain + Gemini 1.5 Pro / GPT-4o-mini |
| Paper search | Semantic Scholar Graph API |
| PDF parsing | PyMuPDF (fitz) |
| State schema | Pydantic / TypedDict |
| Retry logic | Tenacity |

---

## Example Output Flow

```
Topic: "Vision Transformers for medical image segmentation"

Milestone 1:
  ✅ Queries: ["vision transformer medical segmentation", ...]
  ✅ Found 18 candidates → Selected 3 open-access papers
  ✅ Downloaded: abc123.pdf, def456.pdf, ghi789.pdf

Milestone 2:
  ✅ Extracted ~12,000 chars per paper
  ✅ Semantic sections identified: abstract, intro, methods, results, conclusion

Milestone 3:
  ✅ Key findings extracted per paper
  ✅ Cross-comparison: 450 words
  ✅ Abstract, Intro, Methods, Results, Conclusion, References written

Milestone 4:
  ✅ Critique: Overall Quality: Good | Coherence: 7/10
  ✅ Revision applied
  ✅ Final draft ready (2,800 words)
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| No PDFs downloaded | The topic may have few open-access papers. Try a broader topic. |
| `GEMINI_API_KEY` error | Ensure .env is present and key is valid |
| Rate limit from Semantic Scholar | Add `SEMANTIC_SCHOLAR_API_KEY` to .env |
| LangGraph import error | `pip install langgraph --upgrade` |
| Blank sections | LLM sectioning failed; check API key and network |