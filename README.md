# Chatbot-Personal Assistant Project

This project is a chatbot-based personal assistant that uses natural language processing to understand user queries and provide relevant responses. It is built using Python and various libraries such as OpenAI, Langchain for context managment, spaCy for natural language processing, React for the frontend, and FastAPI for the backend.

---

## **Project Goals**

The primary goal of this project is to create a chatbot-based personal assistant that can understand and respond to user queries in a natural language. The assistant should be able to perform various tasks such as answering questions, providing information, and even performing actions based on user commands.

---

## **Features**

1. **Core Features:**
    
    **🧠 Conversational AI:**
    - Uses OpenAI's gpt-4 or gpt-3.5-turbo via API.
    - Maintain context within conversations, allowing multi-turn dialogues.
    - Implement intent recognition to handle specific tasks (e.g., setting reminders, providing weather updates).
    
    **🔗 API Integrations:**
    - Calendar & Reminders: Integrate with Google Calendar/Outlook.
    - Weather Updates: Fetch real-time data using OpenWeather API.
    - Task Automation: Automate emails, notes, and reminders.
    - Web Scraping: Summarize news, stock prices, and more.

    **📢 Voice Interaction:**
    - Input: Use SpeechRecognition to convert speech to text.
    - Output: Use pyttsx3 or gTTS for text-to-speech responses.

    **💾 Persistent Memory:**
    - Store user preferences and conversation history.
    - Use a lightweight database like SQLite or a NoSQL solution like MongoDB.
    - Implement session management to retain context between interactions.

    **🌐 Multi-Platform Support:**
    - Web Interface: Simple front-end with Flask/FastAPI or a more advanced interface with React.
    - Messaging Apps: Integrate with WhatsApp, Slack, or Telegram.


2. **🧪 Advanced Features (Future Enhancements):**
    - Machine Learning Integration: Add predictive analytics or recommendations.
    - Task Automation: Automate repetitive tasks, e.g., sending emails, generating reports.
    - Custom Knowledge Base: Allow the assistant to learn from specific documents or websites.


### Current Features



### Future Enhancements


---

## **Project Structure**

```bash
|-- README.md
|-- backend
|   |-- Dockerfile
|   |-- __init__.py
|   |-- app.py
|   |-- config.py
|   |-- database
|   |-- models
|   |-- requirements.txt
|   |-- routes
|   |   |-- __init__.py
|   |   `-- chat.py
|   |-- services
|   |   |-- __init__.py
|   |   `-- openai_service.py
|   |-- tests
|   `-- websocket
|-- docker-compose.yml
|-- frontend
|   |-- README.md
|   |-- eslint.config.js
|   |-- index.html
|   |-- package-lock.json
|   |-- package.json
|   |-- public
|   |   `-- vite.svg
|   |-- src
|   |   |-- App.css
|   |   |-- App.jsx
|   |   |-- assets
|   |   |   `-- react.svg
|   |   |-- components
|   |   |   |-- ChatWindow.jsx
|   |   |   |-- InputBox.jsx
|   |   |   `-- Message.jsx
|   |   |-- index.css
|   |   |-- main.jsx
|   |   |-- services
|   |   |   `-- api.js
|   |   `-- styles.css
|   `-- vite.config.js
`-- tree.txt
```

---

## **Setup and Usage**

### **1. Clone the Repository**
```bash
git clone https://github.com/shafin-jadavji/chatbot-assistant.git
cd chatbot-assistant

```
### **2. Set Up the BackEnd Environment**
Create a virtual environment and install dependencies:

```bash
cd backend
python -m venv chat_env
source chat_env/bin/activate  # On Windows, use chat_env\Scripts\activate
pip install -r requirements.txt
```
Create a .env file in the backend directory and add your API keys:

```bash
OPENAI_API_KEY=<your_openai_api_key>
WEATHER_API_KEY=<your_weather_api_key>
NEWS_API_KEY=<your_news_api_key>
```

### **3. Set Up the FrontEnd Environment**
```bash
cd frontend
npm install
```

**4. Start Frontend & Backend Servers**

### Start backend:
```bash
cd backend
uvicorn app:app --reload
```
### Start frontend:
```bash
cd frontend
npm run dev
```
---

## **Dependencies**
This project uses the following libraries:

- OpenAI
- Langchain
- spaCy
- React
- FastAPI
- NPM
- Other dependencies are listed in the requirements.txt file.

Install backend dependencies using:
```bash
pip install -r requirements.txt
```

---

## **License**
This project is licensed under the MIT License. See the LICENSE file for details.

---
