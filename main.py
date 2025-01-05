
import requests
from bs4 import BeautifulSoup
from googletrans import Translator
from transformers import pipeline
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os

# Initialize the translator
translator = Translator()

# Initialize the AI pipeline for sentiment analysis
sentiment_analyzer = pipeline("sentiment-analysis")

# Load or create user settings
SETTINGS_FILE = "user_settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {"language": "ar", "model": "sentiment-analysis"}

def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as file:
        json.dump(settings, file)

# Load settings
settings = load_settings()

def translate_and_process_webpage(url, dest_language, model):
    try:
        # Fetch the webpage content
        response = requests.get(url)
        if response.status_code != 200:
            messagebox.showerror("Error", "Failed to fetch the webpage.")
            return

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all text elements in the HTML
        elements = soup.find_all(string=True)

        # Translate and process each text element
        translated_texts = []
        for element in elements:
            if element.strip():  # Skip empty strings
                try:
                    # Translate the text
                    translated = translator.translate(element.strip(), dest=dest_language).text

                    # Process the translated text with AI
                    if model == "sentiment-analysis":
                        result = sentiment_analyzer(translated)[0]
                        analysis = f"Sentiment: {result['label']} (Confidence: {result['score']:.2f})"
                    else:
                        analysis = "No AI processing selected."

                    # Replace the original text with the translated text
                    element.replace_with(translated)

                    # Save the results
                    translated_texts.append(f"Original: {element.strip()}\nTranslated: {translated}\n{analysis}\n")
                except Exception as e:
                    print(f"Error processing text: {e}")

        # Save the translated HTML to a file
        output_file = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML Files", "*.html")])
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(str(soup))
            messagebox.showinfo("Success", f"Translation and processing complete. File saved as {output_file}")

        # Save the translated texts to a file
        with open('translated_texts.txt', 'w', encoding='utf-8') as file:
            file.write("\n".join(translated_texts))
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Create the main application window
app = tk.Tk()
app.title("Professional Webpage Translator and AI Processor")
app.geometry("600x400")

# Create and place widgets
tk.Label(app, text="Enter the URL of the webpage:").pack(pady=10)
url_entry = tk.Entry(app, width=50)
url_entry.pack(pady=5)

tk.Label(app, text="Select the target language:").pack(pady=10)
language_var = tk.StringVar(value=settings.get("language", "ar"))
language_options = ["ar", "en", "es", "fr", "de"]  # Add more languages as needed
language_menu = ttk.Combobox(app, textvariable=language_var, values=language_options)
language_menu.pack(pady=5)

tk.Label(app, text="Select the AI model:").pack(pady=10)
model_var = tk.StringVar(value=settings.get("model", "sentiment-analysis"))
model_options = ["sentiment-analysis", "none"]  # Add more models as needed
model_menu = ttk.Combobox(app, textvariable=model_var, values=model_options)
model_menu.pack(pady=5)

def start_processing():
    url = url_entry.get()
    dest_language = language_var.get()
    model = model_var.get()

    if url:
        # Save user settings
        settings["language"] = dest_language
        settings["model"] = model
        save_settings(settings)

        translate_and_process_webpage(url, dest_language, model)
    else:
        messagebox.showwarning("Input Error", "Please enter a valid URL.")

tk.Button(app, text="Translate and Process", command=start_processing).pack(pady=20)

# Run the application
app.mainloop()
