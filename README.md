# AI-System-to-automatically-Review-and-Summarize-Research-Papers

@"

\# AI System for Automatic Review and Summarization of Research Papers



\## Overview

This project implements an automated pipeline for reviewing and summarizing academic research papers.  

It focuses on transforminging raw PDF documents into structured sections, extracting key findings, performing cross-paper comparisons, and generating academic-style literature review drafts.



The system is designed with modularity, reproducibility, and clarity in mind.



---



\## System Architecture



\### 1. Per-Paper Processing (LangGraph)

LangGraph is used to orchestrate deterministic, per-paper operations:



\- PDF loading and validation

\- Raw text extraction

\- Text normalization

\- Semantic section extraction using a controlled LLM prompt

\- Section validation

\- Storage of structured sections

\- Key finding extraction



\### 2. Cross-Paper Reasoning

Cross-paper operations are performed after individual papers are processed:



\- Comparative analysis across papers

\- Identification of similarities and differences

\- Automated literature review draft generation



---



\## Technologies Used

\- Python

\- LangGraph

\- LangChain

\- Google Gemini API

\- JSON



---



\## Limitations

\- Free-tier Gemini API rate limits restrict batch processing

\- Semantic extraction relies on explicit section headers

\- Large documents may be truncated to avoid API timeouts



---



\## Author

Pari

"@ | Out-File README.md -Encoding utf8

re.

