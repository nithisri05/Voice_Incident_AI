# Voice Incident AI

An AI-powered **Speech-to-Structured Incident Reporting System** designed for industrial environments.  
The system converts **spoken incident reports into structured data automatically** and stores them for analysis.

It uses **speech recognition, natural language processing, and text-to-speech technologies** to enable **hands-free incident reporting**.

---

# Project Overview

Industrial operators often need to report equipment failures or safety incidents quickly.  
Manual reporting systems are slow and inconvenient.

**Voice Incident AI** allows operators to simply **speak the incident**, and the system automatically:

1. Converts speech to text
2. Extracts structured incident details
3. Stores the report in Excel
4. Generates a spoken confirmation

This enables **fast, accurate, and contactless reporting**.

---

# System Architecture
```
User Speech
↓
Browser Audio Recording
↓
Flask Backend
↓
Speech-to-Text (Whisper)
↓
Hybrid NLP Extraction
(Rule-based + LLM fallback)
↓
Conversation Memory Merge
↓
Validation / Clarification
↓
Excel Report Storage
↓
Text-to-Speech Confirmation
```

---

# ⚙️ Technology Stack

| Component | Technology |
|-----------|------------|
Frontend | HTML, CSS, JavaScript |
Audio Recording | MediaRecorder API |
Backend | Python Flask |
Speech Recognition | OpenAI Whisper |
NLP Extraction | Rule-based + GPT-4.1-nano |
Data Storage | Excel (openpyxl) |
Text-to-Speech | OpenAI TTS |
Session Memory | Flask Session |

---

# Project Structure
```voice_incident_ai
│
├── app
│ └── app.py
│
├── services
│ ├── stt_service.py
│ ├── semantic_service.py
│ └── tts_service.py
│
├── utils
│ └── audio_handler.py
│
├── evaluation
│ ├── evaluation.py
│ ├── ground_truth.txt
│ └── test_audio
│
├── static
│ ├── script.js
│ ├── style.css
│ └── tts_audio
│
├── templates
│ └── index.html
│
├── uploads
│
├── report_storage.py
├── config.py
├── requirements.txt
└── README.md
```


---

# Installation

### 1️ Clone the repository
### 2️ Create virtual environment
### 3️ Install dependencies
### 4️ Configure environment variables
### 5 Running the Application and evaluation file:app.py and evaluation.py

---

# Evaluation

The system was evaluated using the following metrics:

| Metric | Description |
|------|-------------|
WER | Word Error Rate for speech recognition |
RTF | Real-Time Factor for latency |
Extraction Accuracy | Structured data correctness |

