# COGNICAM v2.0 - Advanced Credit Appraisal System

COGNICAM is a premium AI-driven credit appraisal platform designed for modern SME lending. This version features a complete backend overhaul with FastAPI and a stunning, single-file frontend experience.

## 🏗️ Architecture

- **Backend**: FastAPI (Python 3.10+)
- **Database**: SQLite (local persistence)
- **Frontend**: Single-page Architecture (HTML5, Vanilla CSS3, Modern ES6 JS)
- **AI**: SHAP Explainability simulation & Natural Language Field Note Analysis

## 🚀 Quick Start

### 1. Backend Setup
Navigate to the backend directory and install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

Start the FastAPI server:
```bash
python main.py
```
The server will start at `http://127.0.0.1:8000`.

### 2. Frontend Access
Since the frontend is a self-contained SPA, you can simply open it in your browser:
```text
frontend/index.html
```
*Note: For API functionality to work, ensure the backend is running.*

## 🔑 Demo Account
Use the following credentials to explore the system without creating an account:
- **Username**: `demo`
- **Password**: `demo123`

## ✨ Features
- **Dynamic 5Cs Scoring**: Character, Capacity, Capital, Collateral, Conditions.
- **Deep Research Terminal**: Automated simulations of registry and news scans.
- **Explainable AI**: Visual breakdown of how every data point impacts the final score.
- **Responsive Design**: Fully optimized for both desktop and mobile viewing.
- **Glassmorphism UI**: Premium visual effects with real-time blur and depth.

---
*Created for the IIT Hackathon 2025*
