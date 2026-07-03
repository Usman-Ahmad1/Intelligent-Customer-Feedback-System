# 🤖 FeedbackFlow AI
**Intelligent Customer Feedback System with Sentiment Analysis & Automated Email Responses**

![FeedbackFlow AI - Architecture](assets/architecture-flow.png)

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.37.1-red.svg)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3.7-green.svg)](https://www.langchain.com/)
[![Groq](https://img.shields.io/badge/Groq-API-orange.svg)](https://groq.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table of Contents
- [Project Overview](#-project-overview)
- [Objectives](#-objectives)
- [Key Features](#-key-features)
- [Screenshots](#-screenshots)
- [Methodology & Architecture](#-methodology--architecture)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Email Workflow](#-email-workflow)
- [Analytics Dashboard](#-analytics-dashboard)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Project Overview

**FeedbackFlow AI** is a production-ready intelligent customer feedback management system. It automatically analyzes customer feedback using AI, determines sentiment, generates personalized email responses, and triggers appropriate business actions such as support ticket creation.

---

## 📌 Objectives

- Automate sentiment analysis of customer feedback in real-time
- Deliver personalized and professional email responses instantly
- Reduce manual effort in customer support
- Improve customer satisfaction through timely replies
- Provide actionable insights via an interactive analytics dashboard
- Enable smooth escalation for negative feedback

---

## ✨ Key Features

### 🧠 Sentiment Analysis
![Sentiment Analysis](assets/sentiment-analysis.png)

- Classifies feedback as **Positive / Negative / Neutral**
- Uses Groq’s `llama-3.1-8b-instant` model
- Custom prompt engineering for high accuracy

### 📧 Automated Email Responses
![Automated Generated Response](assets/automated-response.png)

- **Positive Feedback**: Warm thank you + request for 5-star review
- **Negative Feedback**: Sincere apology + support ticket creation + escalation

### 📊 Analytics Dashboard
![Analytics Dashboard](assets/analytics-dashboard.png)

- Real-time sentiment distribution charts
- Feedback timeline visualization
- Key metrics and export to CSV
- Searchable feedback history

---

## 🏗️ Methodology & Architecture

![System Architecture Flow](assets/architecture-flow.png)

The system follows a clean modular flow:
1. Feedback Input
2. Sentiment Analysis using LLM
3. LangGraph-based Decision Making
4. Automated Response & Action Execution
5. Analytics & Logging

---

## 🛠️ Tech Stack

| Component       | Technology              | Version    |
|-----------------|-------------------------|------------|
| Framework       | Streamlit               | 1.37.1     |
| LLM Provider    | Groq                    | API        |
| Model           | Llama 3.1 8B Instant    | -          |
| Orchestration   | LangChain + LangGraph   | 0.3.7      |
| Email           | SMTP (Gmail)            | -          |
| Visualization   | Plotly                  | 5.24.1     |
| Data Processing | Pandas                  | 2.2.3      |

---

## 🚀 Installation

```bash
git clone <your-repo-url>
cd FeedbackFlow-AI

python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate

pip install -r requirements.txt
