# 🏡 Housing Price Advisor Chatbot

This project is an AI-powered housing price advisor that predicts whether a landlord's quoted price is reasonable based on housing features in Tokyo, Japan. It uses a trained machine learning model (Linear Regression), FastAPI for backend prediction, and Streamlit for an interactive chatbot frontend.

---

## 📦 Features

- Predicts housing trade price based on user input (area, year, distance to station, etc.)
- Compares prediction with landlord's quoted price
- Streams chatbot responses using Gemini-style logic
- Accepts **district names** (like `"ikebukuro"`) and auto-encodes them
- Easy to extend with advanced ML models

---

## 🔧 Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/housing-chatbot.git
cd housing-chatbot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 🚀 Running the Application
```bash
cd agents
python main.py
```

```bash
streamlit run app.py
```
