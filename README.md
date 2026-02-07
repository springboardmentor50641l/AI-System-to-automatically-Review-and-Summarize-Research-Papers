*Project Overview

This project implements an AI-driven system for automating the literature review process. The system retrieves research papers based on a user-defined topic, extracts and structures their content, identifies key findings, performs cross-paper comparisons, and generates coherent academic literature review drafts using large language models.

*System Workflow

User inputs a research topic

Relevant papers are retrieved via Semantic Scholar API

PDFs are downloaded and organized into timestamp-based directories

Text is extracted and cleaned from PDFs

Papers are semantically sectioned (abstract, methodology, results, etc.)

Key findings are extracted for each paper

Cross-paper comparison identifies shared and unique contributions

A formal literature review draft is generated

* Data Organization

All intermediate and final outputs are stored using unique timestamp identifiers to ensure reproducibility and avoid overwriting previous runs. Each paper and analysis stage is tracked independently.

* Milestone Progress

Milestone 1 (Week 1–2): Automated paper retrieval and dataset preparation 

Milestone 2 (Week 3–4): Text extraction, key-finding extraction, and cross-paper comparison 

Milestone 3 (Week 5–6): Automated literature review draft generations

