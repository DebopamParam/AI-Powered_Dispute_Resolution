---
title: Banking Dispute Resolution System
emoji: 🤖
colorFrom: green
colorTo: gray
pinned: false
sdk: docker
---

# Banking Dispute Resolution System

A prototype system for handling banking disputes with AI-powered insights and priority assignment.

## Features

- AI-powered dispute analysis and priority assignment
- Streamlit-based user interface for customer service representatives
- FastAPI backend with SQLite database
- Deployed on Hugging Face Spaces

## Setup

1. Clone this repository
2. Install dependencies: \pip install -r requirements.txt\
3. Set up environment variables (see \.env.example\)
4. Run the application: \python app/entrypoint.py\

## Docker

To run with Docker:

\\\
docker build -t banking-disputes .
docker run -p 8501:8501 -p 8000:8000 banking-disputes
\\\

## Development

All code is in the \pp\ directory:
- \pi/\ - FastAPI backend
- \i/\ - AI services using Langchain and Gemini
- \rontend/\ - Streamlit UI components
