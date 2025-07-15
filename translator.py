import tkinter as tk
from tkinter import ttk, messagebox
from googletrans import Translator
from gtts import gTTS
from playsound import playsound
import os
import speech_recognition as sr
import threading
import time
import re
from PIL import Image, ImageTk

# ============== Core setup ===============
translator = Translator()
recognizer = sr.Recognizer()
mic_active = False
conversation_mode = False
HISTORY_FILE = "translation_history.txt"

language_codes = {
    "English": "en",
    "Japanese": "ja",
    "Tamil": "ta",
    "Korean": "ko",
    "French": "fr",
    "Chinese (Simplified)": "zh-cn",
    "Hindi": "hi",
    "Malayalam": "ml",
    "Telugu": "te",
    "Kannada": "kn"
}

# ============== GUI Window ==============
app = tk.Tk()
app.title("Xiao Qi - AI Translator 💖")
app.geometry("1000x600")
app.resizable(True, True)

# ============== Load Xiao Qi Images ==============
qi_idle_img = ImageTk.PhotoImage(Image.open("qi_idle.png").resize((180, 220)))
qi_wave_img = ImageTk.PhotoImage(Image.open("qi_wave.png").resize((180, 220)))
qi_listen_img = ImageTk.PhotoImage(Image.open("qi_listen.png").resize((180, 220)))
qi_star_img = ImageTk.PhotoImage(Image.open("qi_star.png").resize((180, 220)))
qi_forget_img = ImageTk.PhotoImage(Image.open("xiao-qi1.png").resize((180, 220)))

# Xiao Qi label
img_label = tk.Label(app, image=qi_wave_img, bg="white")
img_label.place(x=650, y=340)

# ============== Xiao Qi Class ==============
class XiaoQi:
    def __init__(self):
        self.image_label = img_label
    def wave(self):
        self.image_label.config(image=qi_wave_img)
    def happy(self):
        self.image_label.config(image=qi_star_img)
    def angry(self):
        self.image_label.config(image=qi_forget_img)
    def talking(self):
        self.image_label.config(image=qi_wave_img)
    def listen_pose(self):
        self.image_label.config(image=qi_listen_img)

xiao_qi = XiaoQi()
app.after(1000, xiao_qi.wave)

# ============== Core Functions ==============
def speak_text(text, lang_code="en"):
    try:
        sentences = re.split(r'[.!?]', text)
        for sentence in sentences:
            clean = sentence.strip()
            if clean:
                tts = gTTS(text=clean, lang=lang_code)
                tts.save("temp.mp3")
                playsound("temp.mp3")
                os.remove("temp.mp3")
                time.sleep(1.2)
    except Exception as e:
        messagebox.showerror("Speech Error", f"🎤 Couldn't speak: {e}")

def translate_text():
    input_text = input_entry.get("1.0", tk.END).strip()
    target_lang_name = language_var.get()
    target_lang_code = language_codes[target_lang_name]
    if not input_text:
        messagebox.showwarning("🚨 Input Needed", "Please enter something to translate!")
        return
    try:
        result = translator.translate(input_text, dest=target_lang_code)
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, result.text)
        detected_lang.set(f"🧠 Detected: {result.src.upper()}")
        history = f"📝 Original: {input_text}\n🔁 Translated ({target_lang_name}): {result.text}\n---\n"
        history_text.insert(tk.END, history)
        history_text.see(tk.END)
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(history)
        xiao_qi.happy()
    except Exception as e:
        messagebox.showerror("Translation Error", f"❌ Failed to translate: {e}")

def speak_input():
    text = input_entry.get("1.0", tk.END).strip()
    if text:
        speak_text(text, "en")
        xiao_qi.talking()

def speak_translated():
    text = output_text.get("1.0", tk.END).strip()
    target_lang_name = language_var.get()
    lang_code = language_codes[target_lang_name]
    if text:
        speak_text(text, lang_code)
        xiao_qi.talking()

def view_history():
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            history_text.delete("1.0", tk.END)
            history_text.insert(tk.END, content)
    except FileNotFoundError:
        messagebox.showinfo("🕵️ No History", "No translation history yet.")

def clear_history():
    open(HISTORY_FILE, "w", encoding="utf-8").close()
    history_text.delete("1.0", tk.END)
    messagebox.showinfo("🧹 Cleared", "All translation history is cleared!")
    xiao_qi.angry()

# ============== Mic Functions ==============
def listen():
    global mic_active
    with sr.Microphone() as source:
        while mic_active:
            try:
                audio = recognizer.listen(source, timeout=1)
                text = recognizer.recognize_google(audio)
                input_entry.delete("1.0", tk.END)
                input_entry.insert(tk.END, text)
                if conversation_mode:
                    translate_text()
                    speak_translated()
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                status_label.config(text="😵 Couldn't understand...Idiot", fg="#c0392b")
            except sr.RequestError:
                status_label.config(text="🌐 Network issue!", fg="#e74c3c")

def toggle_mic():
    global mic_active
    mic_active = not mic_active
    if mic_active:
        mic_btn.config(text="🔴 MIC ON", bg="#808080", fg="white")
        status_label.config(text="🎧 Listening...", fg="#808080")
        xiao_qi.listen_pose()
        threading.Thread(target=listen, daemon=True).start()
    else:
        mic_btn.config(text="🎙️ MIC OFF", bg="#f0f0f0", fg="#000")
        status_label.config(text="💤 Mic is off", fg="#777")

def toggle_convo():
    global conversation_mode, mic_active
    conversation_mode = not conversation_mode
    if conversation_mode:
        convo_btn.config(text="💬 Convo Mode: ON", bg="#74b9ff")
        status_label.config(text="💬 Listening & replying...", fg="#0984e3")
        xiao_qi.happy()
        if not mic_active:
            mic_active = True
            mic_btn.config(text="🔴 MIC ON", bg="#808080", fg="white")
            xiao_qi.listen_pose()
            threading.Thread(target=listen, daemon=True).start()
    else:
        convo_btn.config(text="💬 Convo Mode: OFF", bg="#dfe6e9")
        status_label.config(text="🔇 Convo mode off", fg="#636e72")
        if mic_active:
            mic_active = False
            mic_btn.config(text="🎙️ MIC OFF", bg="#f0f0f0", fg="#000")
            status_label.config(text="💤 Mic is off", fg="#777")

# ============== GUI Layout ==============
tk.Label(app, text="📝 Enter Text:", font=("Arial", 12)).grid(row=0, column=0, sticky="w", padx=10, pady=5)
input_entry = tk.Text(app, height=4, width=60)
input_entry.grid(row=1, column=0, padx=10)

tk.Button(app, text="🔈 Hear Input", command=speak_input).grid(row=2, column=0, sticky="w", padx=10)

tk.Label(app, text="🌍 Translate to:", font=("Arial", 12)).grid(row=3, column=0, sticky="w", padx=10, pady=5)
language_var = tk.StringVar(value="English")
language_dropdown = ttk.Combobox(app, textvariable=language_var, values=list(language_codes.keys()), width=20, state="readonly")
language_dropdown.grid(row=4, column=0, sticky="w", padx=10)

tk.Button(app, text="🔁 Translate", command=translate_text).grid(row=4, column=0, sticky="e", padx=10)

tk.Label(app, text="🎯 Translated Text:", font=("Arial", 12)).grid(row=5, column=0, sticky="w", padx=10, pady=5)
output_text = tk.Text(app, height=4, width=60)
output_text.grid(row=6, column=0, padx=10)

tk.Button(app, text="🗣️ Speak Output", command=speak_translated).grid(row=7, column=0, sticky="w", padx=10, pady=5)

detected_lang = tk.StringVar()
tk.Label(app, textvariable=detected_lang, font=("Arial", 10, "italic"), fg="#2980b9").grid(row=7, column=0, sticky="e", padx=10)

tk.Label(app, text="📖 Translation History", font=("Arial", 12, "bold")).grid(row=0, column=1, padx=10, pady=5)
history_text = tk.Text(app, height=15, width=45)
history_text.grid(row=1, column=1, rowspan=6, padx=10)

tk.Button(app, text="📜 View History", command=view_history).grid(row=7, column=1, sticky="w", padx=10)
clr_btn = tk.Button(app, text="🗑️ Clear History", command=clear_history)
clr_btn.grid(row=7, column=1, sticky="e", padx=10)
clr_btn.place(x=505, y=340)

mic_btn = tk.Button(app, text="🎙️ MIC OFF", command=toggle_mic, bg="#f0f0f0", fg="#000", padx=10, pady=5)
mic_btn.grid(row=8, column=0, pady=5)

convo_btn = tk.Button(app, text="💬 Convo Mode: OFF", command=toggle_convo, bg="#dfe6e9", padx=10)
convo_btn.grid(row=8, column=1)
convo_btn.place(x=10, y=420)

status_label = tk.Label(app, text="Mic is off", font=("Arial", 10), fg="#7f8c8d")
status_label.grid(row=9, column=0, pady=2)

app.mainloop()
