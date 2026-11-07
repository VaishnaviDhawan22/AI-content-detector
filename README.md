AI Content Detector 🤖

An AI-powered web application that analyzes text messages and chat screenshots to estimate whether the content is AI-generated.

Built using Python, Flask, HTML, CSS, and Google's Gemini API.

✨ Features

- Text Analysis: Paste text and analyze it for AI-generated patterns.
- Screenshot Analysis: Upload chat screenshots in PNG, JPEG, or WEBP format.
- Gemini Integration: Uses Google's Gemini API for AI-assisted content analysis.
- Heuristic Analysis: Combines heuristic scoring with AI analysis.
- Results Dashboard: Displays an estimated AI score, confidence, and explanation.
- Simple Interface: Clean, responsive interface with a space-inspired design.

🛠️ Technologies Used

- Python
- Flask
- HTML5
- CSS3
- JavaScript
- Google Gemini API
- Python-dotenv

📁 Project Structure

ai-content-detector/
│
├── app.py
├── yo.py
├── requirements.txt
├── .env
├── .gitignore
│
└── templates/
    └── index.html

⚙️ Installation and Setup

1. Clone the repository

git clone YOUR_REPOSITORY_URL
cd ai-content-detector

2. Create a virtual environment

python -m venv .venv

3. Activate the environment

Windows PowerShell:

.\.venv\Scripts\Activate.ps1

4. Install dependencies

pip install -r requirements.txt

5. Configure your API key

Create a ".env" file in the project directory:

GEMINI_API_KEY=your_api_key_here

Get your API key from "Google AI Studio" (https://aistudio.google.com/).

6. Run the application

python app.py

Open your browser and visit:

http://127.0.0.1:5000

⚠️ Limitations

- AI detection results are estimates, not definitive proof.
- Short messages may produce unreliable results.
- Results depend on the availability and response of the Gemini API.
- API access may be subject to usage limits.

🎯 Project Goal

The goal of this project is to explore AI integration in web applications, image processing, API communication, and backend development using Python and Flask.

👩‍💻 Author
    VAISHNAVI DHAWAN

Developed as a personal learning project while exploring Python, web development, and Generative AI.