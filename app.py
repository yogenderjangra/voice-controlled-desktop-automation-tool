mport tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import queue
import sys
from io import StringIO
import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
from ecapture import ecapture as ec
import pyjokes
import time
import pywhatkit
from PIL import Image, ImageTk
from urllib.request import urlopen
import json
import pyautogui
import random
import screen_brightness_control as sbc
from tkinter import messagebox
import re

class RedirectText:
    """Redirect print statements to both console and GUI"""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = StringIO()

    def write(self, string):
        self.buffer.write(string)
        # Add to GUI
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.update_idletasks()
        # Also print to console
        sys.__stdout__.write(string)

    def flush(self):
        pass

class VoiceAssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Jarvis Voice Assistant")
        self.root.geometry("900x600")
        self.root.configure(bg='#2c3e50')
        
        # Center the window
        self.center_window()
        
        # Variables
        self.assistant_running = False
        self.assistant_thread = None
        self.assistant = None
        self.stop_event = threading.Event()
        
        # Configure style
        self.setup_styles()
        
        # Create UI
        self.create_widgets()
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Redirect print output
        self.redirect = RedirectText(self.output_text)
        sys.stdout = self.redirect
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-q>', lambda e: self.on_closing())
        self.root.bind('<Control-s>', lambda e: self.start_assistant())
        self.root.bind('<Control-x>', lambda e: self.stop_assistant())
        
    def on_closing(self):
        """Handle window closing event"""
        if self.assistant_running:
            result = messagebox.askyesno("Confirm Exit", 
                                        "Assistant is still running. Are you sure you want to exit?")
            if result:
                self.stop_assistant()
                time.sleep(1)  # Give time for thread to close
                self.root.destroy()
        else:
            self.root.destroy()
        
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'900x600+{x}+{y}')
        
    def setup_styles(self):
        """Configure styles for widgets"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        self.bg_color = '#2c3e50'
        self.fg_color = '#ecf0f1'
        self.accent_color = '#3498db'
        self.success_color = '#27ae60'
        self.danger_color = '#e74c3c'
        self.text_bg = '#34495e'
        
        # Button styles
        style.configure('Start.TButton',
                       background=self.success_color,
                       foreground='white',
                       font=('Arial', 12, 'bold'),
                       padding=10)
        style.map('Start.TButton',
                 background=[('active', '#2ecc71')])
        
        style.configure('Stop.TButton',
                       background=self.danger_color,
                       foreground='white',
                       font=('Arial', 12, 'bold'),
                       padding=10)
        style.map('Stop.TButton',
                 background=[('active', '#c0392b')])
        
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Header Frame
        header_frame = tk.Frame(self.root, bg=self.bg_color, height=100)
        header_frame.pack(fill=tk.X, padx=20, pady=(20,10))
        
        # Title
        title_label = tk.Label(header_frame, 
                              text="🤖 JARVIS VOICE ASSISTANT",
                              font=('Arial', 28, 'bold'),
                              bg=self.bg_color,
                              fg=self.accent_color)
        title_label.pack()
        
        # Subtitle
        subtitle_label = tk.Label(header_frame,
                                 text="Your Personal AI Assistant",
                                 font=('Arial', 14),
                                 bg=self.bg_color,
                                 fg=self.fg_color)
        subtitle_label.pack()
        
        # Status Frame
        status_frame = tk.Frame(self.root, bg=self.bg_color)
        status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.status_label = tk.Label(status_frame,
                                    text="● Status: Stopped",
                                    font=('Arial', 12),
                                    bg=self.bg_color,
                                    fg=self.danger_color)
        self.status_label.pack(side=tk.LEFT)
        
        # Time display
        self.time_label = tk.Label(status_frame,
                                   text="",
                                   font=('Arial', 12),
                                   bg=self.bg_color,
                                   fg=self.fg_color)
        self.time_label.pack(side=tk.RIGHT)
        self.update_time()
        
        # Control Buttons Frame
        control_frame = tk.Frame(self.root, bg=self.bg_color)
        control_frame.pack(pady=30)
        
        # Start Button
        self.start_btn = ttk.Button(control_frame,
                                   text="▶ Start Assistant (Ctrl+S)",
                                   style='Start.TButton',
                                   command=self.start_assistant,
                                   width=25)
        self.start_btn.pack(side=tk.LEFT, padx=10)
        
        # Stop Button
        self.stop_btn = ttk.Button(control_frame,
                                  text="⏹ Stop Assistant (Ctrl+X)",
                                  style='Stop.TButton',
                                  command=self.stop_assistant,
                                  state=tk.DISABLED,
                                  width=25)
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        
        # Console Output Frame
        console_frame = tk.Frame(self.root, bg=self.bg_color)
        console_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10,20))
        
        console_label = tk.Label(console_frame,
                                text="📟 Console Output:",
                                font=('Arial', 12, 'bold'),
                                bg=self.bg_color,
                                fg=self.fg_color,
                                anchor=tk.W)
        console_label.pack(fill=tk.X, pady=(0,5))
        
        # Scrolled Text Widget for output
        self.output_text = scrolledtext.ScrolledText(console_frame,
                                                     wrap=tk.WORD,
                                                     font=('Consolas', 10),
                                                     bg=self.text_bg,
                                                     fg=self.fg_color,
                                                     insertbackground='white',
                                                     height=20)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for different message types
        self.output_text.tag_config('error', foreground='#e74c3c')
        self.output_text.tag_config('success', foreground='#27ae60')
        self.output_text.tag_config('info', foreground='#3498db')
        self.output_text.tag_config('warning', foreground='#f39c12')
        
        # Footer
        footer_frame = tk.Frame(self.root, bg='#34495e', height=30)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        footer_label = tk.Label(footer_frame,
                               text="Created with ❤️ | Voice Assistant Project | Ctrl+S: Start | Ctrl+X: Stop | Ctrl+Q: Quit",
                               font=('Arial', 9),
                               bg='#34495e',
                               fg=self.fg_color)
        footer_label.pack(pady=5)
        
        # Initial message
        self.print_colored("="*60, 'info')
        self.print_colored("JARVIS Voice Assistant Initialized", 'info')
        self.print_colored("Click 'Start Assistant' to begin", 'info')
        self.print_colored("="*60, 'info')
        
    def update_time(self):
        """Update the time display"""
        current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        self.time_label.config(text=f"📅 {current_date} | 🕐 {current_time}")
        self.root.after(1000, self.update_time)
        
    def print_colored(self, text, tag=None):
        """Print colored text to output widget"""
        self.output_text.insert(tk.END, text + "\n", tag)
        self.output_text.see(tk.END)
        self.output_text.update_idletasks()
        
    def start_assistant(self):
        """Start the voice assistant in a separate thread"""
        if self.assistant_running:
            return
            
        self.assistant_running = True
        self.stop_event.clear()
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="● Status: Running", fg=self.success_color)
        
        self.print_colored("="*60, 'success')
        self.print_colored("Assistant Started - Listening for commands...", 'success')
        self.print_colored("="*60, 'success')
        
        # Initialize assistant in separate thread
        self.assistant_thread = threading.Thread(target=self.run_assistant, daemon=True)
        self.assistant_thread.start()
        
    def stop_assistant(self):
        """Stop the voice assistant"""
        if not self.assistant_running:
            return
            
        self.assistant_running = False
        self.stop_event.set()
        
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="● Status: Stopped", fg=self.danger_color)
        
        self.print_colored("="*60, 'warning')
        self.print_colored("Assistant Stopped", 'warning')
        self.print_colored("="*60, 'warning')
        
    def run_assistant(self):
        """Main assistant logic"""
        # Create assistant instance in this thread
        assistant = VoiceAssistant()
        
        # Initial greeting
        assistant.wishMe()
        
        while self.assistant_running and not self.stop_event.is_set():
            try:
                # Voice input
                if self.assistant_running and not self.stop_event.is_set():
                    print("Listening for voice command...")
                    query = assistant.takequery()
                    
                    if query and query.lower() != "none":
                        print(f"Voice command received: {query}")
                        self.process_command(assistant, query.lower())
                
                # Small delay to prevent CPU overload
                time.sleep(0.1)
                
            except Exception as e:
                print(f"❌ Error in assistant loop: {e}")
                time.sleep(1)
            
    def process_command(self, assistant, query):
        """Process voice commands"""
        
        if 'tell me about' in query or 'who is' in query:
            assistant.speak('Searching information, sir.')
            query = query.replace("wikipedia", "").strip()
            try:
                results = wikipedia.summary(query, sentences=4)
                assistant.speak("According to Wikipedia")
                print(results)
                assistant.speak(results)
            except wikipedia.exceptions.DisambiguationError:
                assistant.speak("There are multiple results. Please be more specific.")
            except wikipedia.exceptions.PageError:
                assistant.speak("I couldn't find any information on that.")
            except Exception as e:
                assistant.speak("Sorry, I encountered an error while searching.")
                print(f"Wikipedia error: {e}")

        elif "open wikipedia" in query or "wikipedia" in query:
            assistant.speak('ok sir')
            webbrowser.open_new_tab("https://www.wikipedia.org/")

        elif 'open youtube' in query or "youtube" in query:
            assistant.speak('ok sir, opening youtube')
            webbrowser.open_new_tab("youtube.com")

        elif 'open google' in query or "google" in query:
            assistant.speak('ok sir, opening google')
            webbrowser.open_new_tab("google.com")

        elif 'play music' in query or "music" in query:
            assistant.speak('Yes sir, playing music')
            music_dir = r"D:\songs"
            if os.path.exists(music_dir):
                try:
                    songs = os.listdir(music_dir)
                    if songs:
                        song = random.choice(songs)
                        os.startfile(os.path.join(music_dir, song))
                        print(f"Playing: {song}")
                    else:
                        assistant.speak("No songs found in the directory")
                except Exception as e:
                    print(f"Error playing music: {e}")
                    assistant.speak("Error playing music")
            else:
                assistant.speak("Music directory not found")
                     
        elif 'open stack overflow' in query:
            assistant.speak('ok sir')
            webbrowser.open_new_tab("stackoverflow.com")
        
        elif 'what is the time' in query or 'time' in query:
            strTime = datetime.datetime.now().strftime("%I:%M %p")
            assistant.speak(f"Sir, the time is {strTime}")

        elif 'what is the date' in query or 'date' in query:
            strDate = datetime.datetime.now().strftime("%d %B %Y")
            assistant.speak(f"Sir, the date is {strDate}")

        elif 'tell me the latest news' in query or "tell me the news" in query or "latest news" in query or "news" in query:
            try:
                jsonObj = urlopen("https://newsapi.org/v2/top-headlines?country=in&apiKey=1cc4096fa7db40e4a7cac2638854e4d3")
                data = json.load(jsonObj)
                i = 1
                assistant.speak('here are some top news from the times of india')
                print('''=============== TIMES OF INDIA ============'''+ '\n')
                 
                for item in data['articles']:
                    if i > 4:
                        break   
                    print(str(i) + '. ' + item['title'] + '\n')
                    print(item['description'] + '\n')
                    assistant.speak(str(i) + '. ' + item['title'] + '\n')
                    i += 1
            except Exception as e:
                print(str(e))
                assistant.speak("Sorry, I couldn't fetch the news at this moment.")

        elif 'play' in query and not any(x in query for x in ['music', 'youtube']):
            song = query.replace('play', '').strip()
            if song:
                assistant.speak('playing ' + song)
                print(f"Playing {song} on YouTube")
                youtube_thread = threading.Thread(target=pywhatkit.playonyt, args=(song,), daemon=True)
                youtube_thread.start()
            else:
                assistant.speak("What would you like me to play?")

        elif 'jarvis' in query:
            assistant.speak('yes sir')

        elif 'how are you' in query or "hu r u" in query:
            assistant.speak('I am fine sir, thank you for asking')
            assistant.speak('how are you sir')

        elif 'fine' in query or "good" in query:
            assistant.speak("It's good to know that you're fine, how i can help you")

        elif 'what are you doing' in query:
            assistant.speak('nothing sir')

        elif 'what is your use' in query:
            assistant.speak('i am designed to, minimise human work by, automation')

        elif "who are you" in query:
            assistant.speak("I am a virtual assistant. I am programmed to minor tasks, like, opening youtube, google, gmail and many more, predict time, take a photo, searching information on browser and wikipedia also, predict weather in different cities, get top headline news from times of india, and you can ask me computational or geographical questions too!")

        elif "who made you" in query or "who created you" in query:
            assistant.speak("I have been created by, Yash, and his team.")

        elif 'reason for you' in query:
            assistant.speak("I was created as a Minor project by Mr yash ")

        elif "why you came to world" in query:
            assistant.speak("Thanks to YASH. further It's a secret")

        elif "thank you" in query:
            assistant.speak("wost welcome sir !")

        elif 'are you single' in query:
            assistant.speak("I am in a relationship with wifi")

        elif "joke" in query:
            try:
                joke = pyjokes.get_joke()
                print(joke)
                assistant.speak(joke)
            except:
                assistant.speak("Sorry, I couldn't think of a joke right now.")

        elif 'write a note' in query:
            assistant.speak("What should i write, sir")
            note = assistant.takequery()
            if note != "None":
                file = open('jarvis.txt', 'w')
                assistant.speak("Sir, Should i include date and time")
                snfm = assistant.takequery()
                assistant.speak("Ok sir")
                if 'yes' in snfm or 'sure' in snfm:
                    strTime = datetime.datetime.now().strftime("%H:%M:%S")
                    file.write(strTime)
                    file.write(" :- ")
                    file.write(note)
                else:
                    file.write(note)
                file.close()
                assistant.speak("Note saved successfully")
         
        elif "tell me the note" in query or "tell the note" in query:
            assistant.speak("yes sir, telling Notes")
            try:
                file = open("jarvis.txt", "r")
                content = file.read()
                if content:
                    assistant.speak(content)
                else:
                    assistant.speak("No notes found")
                file.close()
            except:
                assistant.speak("No notes found")

        elif 'open code' in query or "vs code" in query:
            assistant.speak('Ok sir, opening VS Code')
            os.system("start code")

        elif 'open powerpoint' in query:
            assistant.speak('Ok sir, opening PowerPoint')
            os.system("start powerpnt")
        
        elif 'open excel' in query:
            assistant.speak('Ok sir, opening Excel')
            os.system("start excel")
        
        elif 'open paint' in query:
            assistant.speak('Ok sir, opening paint')
            os.system("start mspaint")

        elif 'open word' in query:
            assistant.speak('Ok sir, opening Word')
            os.system("start winword")
        
        elif 'open spotify' in query:
            assistant.speak('Ok sir, opening Spotify')
            os.system("start spotify")
        
        elif 'open telegram' in query:
            assistant.speak('Ok sir, opening Telegram')
            os.system("start telegram")
        
        elif 'open camera' in query:
            assistant.speak('Opening camera')
            os.system("start microsoft.windows.camera:")
        
        elif 'open calculator' in query:
            assistant.speak('Opening calculator')
            os.system("start calc")
        
        elif 'open notepad' in query:
            assistant.speak('Opening notepad')
            os.system("start notepad")
        
        elif 'open command prompt' in query:
            assistant.speak('Opening command prompt')
            os.system("start cmd")
        
        elif 'open task manager' in query:
            assistant.speak('Opening task manager')
            os.system("start taskmgr")

        elif 'open my pc' in query or 'open this pc' in query:
            assistant.speak('Opening This PC')
            os.system("start explorer")
        
        elif 'open documents' in query:
            assistant.speak('Opening documents')
            os.system("start shell:documents")
        
        elif 'open downloads' in query:
            assistant.speak('Opening downloads')
            os.system("start shell:downloads")
        
        elif 'open desktop' in query:
            assistant.speak('Opening desktop')
            os.system("start shell:desktop")
        
        elif 'open local disk d' in query or 'open d drive' in query:
            assistant.speak('Opening local disk D')
            os.system("start D:")
        
        elif 'open local disk c' in query or 'open c drive' in query:
            assistant.speak('Opening local disk C')
            os.system("start C:")
        
        elif 'open brave browser' in query or 'open brave' in query:
            assistant.speak('Opening Brave browser')
            os.system("start brave")

        elif 'open chrome' in query:
            assistant.speak('Opening Chrome')
            os.system("start chrome")

        elif 'open edge' in query:
            assistant.speak('Opening Microsoft Edge')
            os.system("start msedge")

        elif 'take a photo' in query or "take a selfie" in query:
            assistant.speak('ok sir , taking photo')
            try:
                ec.capture(0, "Jarvis Camera ", "img.jpg")
                assistant.speak("Photo taken successfully")
            except:
                assistant.speak("Sorry, I couldn't take a photo")

        elif "where is" in query:
            query = query.replace("where is", "")
            location = query.strip()
            assistant.speak("It is located in ")
            assistant.speak(location)
            webbrowser.open_new_tab("https://www.google.com/maps/place/" + location + "")

        elif 'search about' in query or 'how to make' in query or "who is" in query:
            assistant.speak('here it is the result sir')
            query = query.replace("search", "").replace("about", "").strip()
            webbrowser.open_new_tab("https://www.google.com/search?q=" + query)

        elif "switch the window" in query or "switch window" in query:
            assistant.speak("Okay sir, Switching the window")
            pyautogui.keyDown("alt")
            pyautogui.press("tab")
            time.sleep(1)
            pyautogui.keyUp("alt")
        
        elif 'volume up' in query:
            for i in range(5):
                pyautogui.press("volumeup")
            print("Volume increased")
        
        elif 'volume down' in query:
            for i in range(5):
                pyautogui.press("volumedown")
            print("Volume decreased")
        
        elif 'mute volume' in query:
            pyautogui.press("volumemute")    
            assistant.speak("Volume muted")

        elif 'unmute volume' in query or 'unmute' in query:
            assistant.speak('Unmuting the volume')
            pyautogui.press("volumemute")
        
        elif 'brightness low' in query or 'dim screen' in query:
            assistant.speak("Setting brightness to low")
            try:
                sbc.set_brightness(30)
            except:
                assistant.speak("Could not adjust brightness")

        elif 'brightness high' in query or 'full brightness' in query:
            assistant.speak("Setting brightness to high")
            try:
                sbc.set_brightness(100)
            except:
                assistant.speak("Could not adjust brightness")

        elif 'stop' in query or 'exit' in query or 'quit' in query:
            assistant.speak('OK sir, shutting down')
            self.root.after(0, self.stop_assistant)

class VoiceAssistant:
    """VoiceAssistant class"""
    
    def __init__(self):
        self.engine = None
        self.init_engine()
        
    def init_engine(self):
        """Initialize pyttsx3 engine in the current thread"""
        try:
            self.engine = pyttsx3.init('sapi5')
            self.voices = self.engine.getProperty('voices')
            self.engine.setProperty('voice', self.voices[0].id)
        except Exception as e:
            print(f"Error initializing speech engine: {e}")

    def speak(self, audio):
        """Thread-safe speak method"""
        try:
            if self.engine is None:
                self.init_engine()
            
            print(f"JARVIS: {audio}")
            self.engine.say(audio)
            self.engine.runAndWait()
        except RuntimeError as e:
            print(f"Speech error (retrying): {e}")
            try:
                self.engine = pyttsx3.init('sapi5')
                self.voices = self.engine.getProperty('voices')
                self.engine.setProperty('voice', self.voices[0].id)
                self.engine.say(audio)
                self.engine.runAndWait()
            except Exception as e2:
                print(f"Failed to speak after retry: {e2}")
        except Exception as e:
            print(f"Error in speak method: {e}")

    def wishMe(self):
        hour = int(datetime.datetime.now().hour)
        if 0 <= hour < 12:
            self.speak("Good Morning, Sir!")
        elif 12 <= hour < 18:
            self.speak("Good Afternoon, Sir!")
        else:
            self.speak("Good Evening, Sir!")

        self.speak("How can I help you?")
 
    def takequery(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            r.pause_threshold = 1
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source)

        try:
            print("Recognizing...")
            query = r.recognize_google(audio, language='en-in')
            print(f"User said: {query}\n")
            return query
        except sr.UnknownValueError:
            print("Could not understand audio")
            return "None"
        except sr.RequestError:
            print("Could not request results")
            return "None"
        except Exception as e:
            print(f"Error in recognition: {e}")
            return "None"

def main():
    root = tk.Tk()
    app = VoiceAssistantGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
