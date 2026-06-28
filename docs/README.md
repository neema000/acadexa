# Acadexa — Voice-Controlled LMS (Starter)

Overview

Acadexa is a Final Year Project (FYP) that provides an AI-powered, voice-enabled Learning Management System (LMS). It allows users to interact with the system using voice commands while providing intelligent responses through NLP and an LLM-based fallback mechanism for complex queries.

Project Type: Final Year Project (Team of Two)

Features
Voice-enabled user interaction
NLP-based intent recognition
LLM fallback for complex or unanswered queries
FastAPI REST APIs
Student and course management
PostgreSQL database integration
Modular backend architecture

Tech Stack
Backend
Python
FastAPI
SQLAlchemy
Database
PostgreSQL
AI / NLP
Rule-based NLP
Large Language Model (LLM) fallback
Frontend
HTML
CSS
JavaScript
React.js
TypeScript

Installation
Clone the repository
git clone https://github.com/neema000/acadexa.git
cd acadexa
Create a virtual environment
python -m venv venv
Activate

Windows

venv\Scripts\activate

Linux / macOS

source venv/bin/activate
Install dependencies
pip install -r requirements.txt
Configure environment variables
Create a .env file using .env.example.

Run the backend
uvicorn backend.main:app --reload

My Contributions

This repository showcases my contributions to the project, including:

FastAPI backend development
REST API implementation
PostgreSQL integration
LLM integration for complex query handling
Voice query processing
Backend testing and debugging
Team

This project was developed as a Final Year Project by a team of two members. This repository highlights my implementation and contributions while preserving the collaborative nature of the project.

## Structure
- backend/  — FastAPI app
- nlp/      — intent parsing rules
- web/      — frontend demo
- db/       — schema & seed
- docs/     — documentation

Future Improvements
Semantic search using vector embeddings
Text-to-speech responses
Multi-language support
Advanced analytics dashboard
License

This project is intended for educational and portfolio purposes.
