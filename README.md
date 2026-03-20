# 🤖 Jarvis Voice Assistant
🤖 Jarvis Voice Assistant (GUI Based)

A Python-based GUI Voice Assistant inspired by Jarvis, built using Tkinter and various Python libraries. This assistant can perform tasks like voice commands, opening apps, playing music, searching the web, telling jokes, controlling volume/brightness, and more.

🚀 Features

🎤 Voice Recognition (Speech-to-Text)

🔊 Text-to-Speech (Jarvis speaks back)

🖥️ GUI Interface (Tkinter based)

🌐 Open Websites (Google, YouTube, Wikipedia)

🎵 Play Music (Local + YouTube)

📰 Fetch Latest News

😂 Tell Jokes

📝 Write & Read Notes

📂 Open System Apps (VS Code, Notepad, Chrome, etc.)

📸 Take Photos using Camera

🔊 Volume Control

💡 Brightness Control

🗺️ Location Search on Maps

🛠️ Technologies Used

Python

Tkinter (GUI)

pyttsx3 (Text-to-Speech)

SpeechRecognition (Voice Input)

Wikipedia API

pywhatkit

pyautogui

PIL (Image Processing)

screen_brightness_control

📦 Installation
Step 1: Clone the Repository
git clone https://github.com/your-username/jarvis-voice-assistant.git
cd jarvis-voice-assistant
Step 2: Install Required Libraries

pip install pyttsx3 speechrecognition wikipedia pywhatkit pyjokes pyautogui pillow screen-brightness-control ecapture

Also install:

pip install pyaudio

⚠️ If PyAudio fails:

Windows: Download .whl file and install manually

▶️ How to Run
python gui_jarvis.py
🎮 Controls

▶ Start Assistant → Start listening

⏹ Stop Assistant → Stop assistant

⌨️ Shortcuts:

Ctrl + S → Start

Ctrl + X → Stop

Ctrl + Q → Quit

🧠 Sample Voice Commands

"Open YouTube"

"Play music"

"What is the time"

"Tell me a joke"

"Search about Python"

"Open Chrome"

"Take a photo"

"Volume up"

"Brightness high"

📁 Project Structure
jarvis-voice-assistant/
│
├── gui_jarvis.py     # Main GUI file
├── jarvis.txt        # Notes file (auto-created)
├── README.md         # Project documentation
⚠️ Notes

Make sure your microphone is working properly

Internet connection is required for:

Voice recognition

Wikipedia

News

YouTube playback

Update the music directory path in code:

music_dir = "D:\\songs"
💡 Future Improvements
