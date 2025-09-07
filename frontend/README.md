
# 🎯 PS Solution Submission — Conversational Agent Framework for Customer Onboarding

## 🚀 Objective

Build an agentic Live Sales Assistant where multiple specialized agents work together to:
- Fetch trustworthy public domain & personal intelligence
- Convert meeting audio into structured context
- Continuously produce contextual, timely talking points
- Explain which agent did what with provenance and an interactive “who’s thinking now” UI

The system is designed to be pilot-ready, explainable, and robust against degraded third-party APIs.

---

## 🏗️ Folder Structure

```
.
├── domain_agent.py
├── entity_agent.py
├── planner_agent.py
├── ranking_agent.py
├── retriever_agent.py
├── stt_agent.py
├── ui_agent.py
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   ├── vite.config.js
│   └── ...
├── requirements.txt
├── docker-compose.yml
├── results/           # Stores generated reports and files
├── uploads/           # Temporary storage for uploaded files
├── .env               # Environment configuration (optional)
├── README.md          # This file
```

---

## 🛠️ How to Run the Solution

### Step 1: Create and Activate Virtual Environment

```bash
mkdir ps_solution
cd ps_solution

python3 -m venv venv

# Activate environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt
```

---

### Step 2: Run Agents

Open six separate terminals and run:

```bash
python ui_agent.py
python ranking_agent.py
python planner_agent.py
python domain_agent.py
python retriever_agent.py
python entity_agent.py
```

---

### Step 3: Start Frontend Web Interface

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at:  
👉 http://localhost:5173

---

### Step 4: Run Speech-to-Text (STT) Agent

```bash
python stt_agent.py
```

This agent listens for user audio input and processes it.

---

## ⚡ Usage Workflow

1. Start all six agents in separate terminals.
2. Launch the frontend web interface.
3. Start the STT agent for speech input.
4. Interact with the web interface.
5. Receive intelligent, explainable onboarding assistance.
6. Provenance metadata will be shown in the UI.

---

## 📚 Deliverables

- Modular microservice agent architecture
- Transparent provenance tracking
- Scalable solution design
- Pilot-ready user interface

---

## ✅ Contact

For any questions or support, please contact:  
👤 Kanhaiya and Manish  
🏷️ Team XYZ

---

Thank you for evaluating our PS Hackathon solution 🚀
