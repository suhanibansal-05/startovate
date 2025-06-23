🚀 Startovate - Your AI-Powered Startup Idea Generator
Startovate is an intuitive, AI-driven web application built with Streamlit that helps aspiring entrepreneurs and innovators generate, develop, and articulate their next big startup idea. Whether you're looking for a fresh concept, a quick pitch, or just some inspiration, Startovate has you covered.

✨ Features

Intelligent Idea Generation: Get unique startup ideas tailored to your selections, including industry, target audience, technology, goals, and more.

Instant Pitch Deck Creation: Automatically generate a concise and compelling pitch deck based on your generated idea, outlining the problem, solution, market, business model, and feasibility.

AI Voice Narration (Text-to-Speech): Listen to your generated ideas and full pitch decks narrated by an AI voice, perfect for practicing your pitch or getting a feel for the presentation.

Voice Suggestions (Speech-to-Text): Record your thoughts or feedback directly into the app using your voice.

User Authentication System: Securely log in, sign up, and manage your personalized experience.

Idea Gallery: Save your favorite generated startup ideas to your personal gallery for future reference and easy access.

Pitch Deck PDF Download: Download your generated pitch decks as professional PDF documents.

Email Integration: Easily send your generated startup ideas to your email address.



🧠 How it Works
Startovate combines user input with a carefully designed logic to simulate AI-driven idea generation. By selecting various parameters like industry, audience, and technology, the app crafts unique startup names, taglines, core ideas, and monetization strategies. It then structures this information into a coherent pitch deck. The integrated voice features (pyttsx3 for TTS and speech_recognition for STT) add a dynamic, multi-modal layer to the user experience.

🛠️ Technologies Used

Streamlit: The primary framework for building the interactive web application.

Python: The core programming language.

pyttsx3: For text-to-speech functionality (AI voice narration).

speech_recognition: For speech-to-text capabilities (recording suggestions).

smtplib & email.message: For sending email notifications with generated ideas.

reportlab: To generate and download pitch decks as PDF files.

json: For user data and saved ideas persistence.

hashlib: For securely hashing user passwords.

pyautogui (for Linux menu integration, if any part of that project is merged here)

pywhatkit (for Linux menu integration, if any part of that project is merged here)

time: For managing delays and smooth transitions.

re: For regular expression operations (e.g., cleaning text for TTS).



🚀 Installation & Setup
Prerequisites:

Python 3.x: Ensure Python is installed on your system.
A stable internet connection for voice recognition services and email.
Gmail App Password: If you use Gmail for sending emails via smtplib, you will need to generate an "App Password" as regular password authentication is often blocked for security reasons.
Clone the Repository:

Bash

git clone https://github.com/your-username/startovate.git
cd startovate
(Replace your-username with your GitHub username.)

Create a Virtual Environment (Recommended):

Bash

python -m venv venv
# On Windows
.\venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
Install Dependencies:

Bash

pip install -r requirements.txt
(If you don't have a requirements.txt, you can create one by running pip freeze > requirements.txt after installing the listed libraries manually, or simply install them one by one:
pip install streamlit pyttsx3 SpeechRecognition reportlab)

Configure Email (Optional):

Open the send_idea_email function in your strt.py (or main app file).
Replace 'saniyakhandelwal10446@gmail.com' with your sending email address.
Replace 'vtob imzt pojv fmmg' with your generated App Password.
