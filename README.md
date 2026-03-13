# Agentic AI Agent Generator 🤖

An **Agentic AI system that generates AI agents from a user prompt.**
This project allows users to describe what kind of AI agent they want, and the system automatically generates the **code, structure, and logic** required to build that agent.

---

## 🚀 Features

* 🧠 Prompt-based **AI Agent generation**
* ⚙️ Automatically creates **agent logic and structure**
* 📦 Modular project architecture
* 🔄 Follow-up generation with stored interactions
* 🗂 SQLite database for tracking generated agents
* 🧩 Extensible architecture for building custom agents

---

## 🏗 Project Structure

```
Agentic_AI_Agent_Generator
│
├── app/                # Core application logic
├── deploy/             # Deployment-related files
├── main.py             # Entry point of the application
├── requirements.txt    # Project dependencies
├── followup_data.db    # SQLite database
├── .gitignore
└── README.md
```

---

## ⚙️ Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/mayur2580/Agentic_AI_Agent_Generator.git
cd Agentic_AI_Agent_Generator
```

### 2️⃣ Create a virtual environment

```bash
python -m venv myenv
```

Activate it:

**Windows**

```bash
myenv\Scripts\activate
```

**Mac/Linux**

```bash
source myenv/bin/activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Project

Start the application:

```bash
python main.py
```

The system will prompt you to **enter a description of the AI agent** you want to generate.

Example prompt:

```
Create an AI agent that summarizes PDF documents.
```

The generator will produce the **agent structure and code** automatically.

---

## 🧠 How It Works

1. User enters a **prompt describing an AI agent**
2. The system processes the request
3. Agent logic and structure are generated
4. Generated agent data is stored for follow-up interactions

---

## 🔧 Technologies Used

* Python
* AI/LLM Integration
* SQLite
* Modular Agent Architecture

---

## 📌 Future Improvements

* Web UI for generating agents
* Support for multiple LLM providers
* Auto-deployment of generated agents
* Integration with LangGraph workflows


