import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from gtts import gTTS
from playsound import playsound
import os
import tempfile
import time
import threading

class VoiceToTextApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Story Voicalizer")

        # Text input
        self.text_label = tk.Label(root, text="Enter your story:")
        self.text_label.pack(pady=10)
        self.text_entry = tk.Text(root, wrap='word', height=10, width=50)
        self.text_entry.pack(pady=10)

        # Enable standard shortcuts
        self.text_entry.bind("<Control-a>", self.select_all)
        self.text_entry.bind("<Control-c>", self.copy)
        self.text_entry.bind("<Control-x>", self.cut)
        self.text_entry.bind("<Control-v>", self.paste)

        # Voice selection
        self.voice_label = tk.Label(root, text="Select voice:")
        self.voice_label.pack(pady=10)
        self.voice_option = ttk.Combobox(root, values=["en", "en-au", "en-uk", "en-us"])
        self.voice_option.set("en")
        self.voice_option.pack(pady=10)

        # Speech rate slider
        self.rate_label = tk.Label(root, text="Speech rate (words per minute):")
        self.rate_label.pack(pady=5)
        self.rate_scale = ttk.Scale(root, from_=100, to=250, orient='horizontal', length=200)
        self.rate_scale.set(175)  # Default value
        self.rate_scale.pack(pady=5)
        self.rate_value_label = tk.Label(root, text="175 WPM")
        self.rate_value_label.pack(pady=5)
        self.rate_scale.configure(command=self.update_rate_label)

        # File name input
        self.file_name_label = tk.Label(root, text="Enter file name (without extension):")
        self.file_name_label.pack(pady=10)
        self.file_name_entry = tk.Entry(root, width=30)
        self.file_name_entry.pack(pady=10)

        # Convert and play button
        self.convert_play_button = tk.Button(root, text="Play", command=self.convert_and_play_threaded)
        self.convert_play_button.pack(pady=10)

        # Convert and save button
        self.convert_save_button = tk.Button(root, text="Convert and Save", command=self.convert_and_save_threaded)
        self.convert_save_button.pack(pady=10)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(root, orient="horizontal", length=200, mode="determinate", variable=self.progress_var)
        self.progress.pack(pady=10)
        self.progress_label = tk.Label(root, text="0%")
        self.progress_label.pack(pady=5)

        # Add a cancel button
        self.cancel_button = tk.Button(root, text="Cancel", command=self.cancel_operation, state=tk.DISABLED)
        self.cancel_button.pack(pady=10)

        self.current_thread = None
        self.cancel_flag = threading.Event()

    def select_all(self, event):
        self.text_entry.tag_add(tk.SEL, "1.0", tk.END)
        self.text_entry.mark_set(tk.INSERT, "1.0")
        self.text_entry.see(tk.INSERT)
        return 'break'

    def copy(self, event):
        if self.text_entry.tag_ranges(tk.SEL):
            self.text_entry.event_generate("<<Copy>>")
        return 'break'

    def cut(self, event):
        if self.text_entry.tag_ranges(tk.SEL):
            self.text_entry.event_generate("<<Cut>>")
        return 'break'

    def paste(self, event):
        self.text_entry.event_generate("<<Paste>>")
        return 'break'

    def update_rate_label(self, value):
        wpm = int(float(value))
        self.rate_value_label.config(text=f"{wpm} WPM")

    def update_progress(self, progress):
        self.progress_var.set(progress)
        self.progress_label.config(text=f"{progress:.1f}%")
        self.root.update_idletasks()

    def convert_to_speech(self, save_path=None):
        text = self.text_entry.get("1.0", tk.END).strip()
        if not text:
            self.root.after(0, lambda: messagebox.showerror("Error", "Please enter a story to convert."))
            return None

        voice = self.voice_option.get()
        words_per_minute = int(self.rate_scale.get())
        speed = 'slow' if words_per_minute <= 175 else 'fast'

        max_retries = 3
        for attempt in range(max_retries):
            try:
                if self.cancel_flag.is_set():
                    return None

                self.root.after(0, lambda: self.update_progress(5))

                tts = gTTS(text=text, lang=voice, slow=(speed == 'slow'))

                if self.cancel_flag.is_set():
                    return None

                self.root.after(0, lambda: self.update_progress(30))

                if save_path:
                    tts.save(save_path)
                    self.root.after(0, lambda: self.update_progress(100))
                    return save_path
                else:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                        temp_path = temp_file.name
                    tts.save(temp_path)
                    self.root.after(0, lambda: self.update_progress(100))
                    return temp_path
            except Exception as e:
                if attempt < max_retries - 1 and not self.cancel_flag.is_set():
                    time.sleep(1)
                else:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to convert text to speech after {max_retries} attempts. Error: {str(e)}"))
                    return None

    def convert_and_play_threaded(self):
        self.start_operation()
        self.current_thread = threading.Thread(target=self.convert_and_play, daemon=True)
        self.current_thread.start()

    def convert_and_play(self):
        temp_file = self.convert_to_speech()
        if temp_file and not self.cancel_flag.is_set():
            try:
                playsound(temp_file)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to play audio. Error: {str(e)}"))
            finally:
                os.remove(temp_file)
        self.end_operation()

    def convert_and_save_threaded(self):
        self.start_operation()
        self.current_thread = threading.Thread(target=self.convert_and_save, daemon=True)
        self.current_thread.start()

    def convert_and_save(self):
        file_name = self.file_name_entry.get().strip()
        if not file_name:
            self.root.after(0, lambda: messagebox.showerror("Error", "Please enter a file name."))
            self.end_operation()
            return

        file_name += ".mp3"
        save_path = filedialog.asksaveasfilename(defaultextension=".mp3",
                                                 filetypes=[("MP3 files", "*.mp3")],
                                                 initialfile=file_name)
        if save_path and not self.cancel_flag.is_set():
            saved_file = self.convert_to_speech(save_path)
            if saved_file:
                self.root.after(0, lambda: messagebox.showinfo("Success", f"File saved successfully as:\n{saved_file}"))
        self.end_operation()

    def start_operation(self):
        self.progress_var.set(0)
        self.cancel_flag.clear()
        self.convert_play_button.config(state=tk.DISABLED)
        self.convert_save_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)

    def end_operation(self):
        self.convert_play_button.config(state=tk.NORMAL)
        self.convert_save_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self.progress_label.config(text="0%")

    def cancel_operation(self):
        self.cancel_flag.set()
        if self.current_thread:
            self.current_thread.join(timeout=1)
        self.end_operation()

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceToTextApp(root)
    root.mainloop()
