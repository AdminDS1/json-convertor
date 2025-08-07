import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import json
import pyperclip
import re
from PIL import Image
from customtkinter import CTkImage
import threading
import time
import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS 
    except Exception:
        base_path = os.path.abspath(".") 
    return os.path.join(base_path, relative_path)

def clean_whitespace(text):
    text = text.strip()
    text = re.sub(r'\n\s*\n+', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = text.replace('\n', ' ')
    return text

def remove_tags(code, tags):
    for tag in tags:
        code = re.sub(f"</?{tag}[^>]*>", "", code, flags=re.IGNORECASE)
    return code.strip()

def minify_css(css_code):
    css_code = re.sub(r'/\*.*?\*/', '', css_code)
    css_code = re.sub(r'\s*([{}:;,])\s*', r'\1', css_code)
    css_code = re.sub(r'\s+', ' ', css_code)
    return css_code.strip()

def minify_js(js_code):
    js_code = re.sub(r'//.*', '', js_code)
    js_code = re.sub(r'/\*[\s\S]*?\*/', '', js_code)
    js_code = re.sub(r'\s*([{}();,:=+\-*/<>])\s*', r'\1', js_code)
    js_code = re.sub(r'\s+', ' ', js_code)
    return js_code.strip()

def validate_code(code_type, code):
    """Kod validation için basit kontrol"""
    if code_type == "css" and code.strip():
        return "✓ Geçerli CSS" if "{" in code or ":" in code else "⚠ CSS formatı belirsiz"
    elif code_type == "html" and code.strip():
        return "✓ Geçerli HTML" if "<" in code and ">" in code else "⚠ HTML formatı belirsiz"
    elif code_type == "js" and code.strip():
        return "✓ Geçerli JavaScript" if any(x in code for x in ["function", "var", "let", "const", "=", ";"]) else "⚠ JavaScript formatı belirsiz"
    return "○ Boş"

update_timer = None
def on_any_input_change(event=None):
    global update_timer
    
    if update_timer:
        app.after_cancel(update_timer)
    
    update_timer = app.after(300, update_json_output)

def update_json_output():
    try:
        html_raw = html_textbox.get("1.0", tk.END)
        css_raw = css_textbox.get("1.0", tk.END)
        js_raw = js_textbox.get("1.0", tk.END)

        html_code = clean_whitespace(remove_tags(html_raw, ["html", "body"]))
        css_code = minify_css(remove_tags(css_raw, ["style"]))
        js_code = minify_js(remove_tags(js_raw, ["script"]))

        css_status_label.configure(text=validate_code("css", css_code))
        html_status_label.configure(text=validate_code("html", html_code))
        js_status_label.configure(text=validate_code("js", js_code))

        data = {
            "html": html_code,
            "css": css_code,
            "js": js_code
        }

        json_output = json.dumps(data, ensure_ascii=False, indent=2)
        output_textbox.configure(state="normal")
        output_textbox.delete("1.0", tk.END)
        output_textbox.insert(tk.END, json_output)
        output_textbox.configure(state="disabled")
        
        char_count = len(json_output)
        char_count_label.configure(text=f"Toplam karakter: {char_count:,}")
        
    except Exception as e:
        print(f"Update error: {e}")

def copy_to_clipboard():
    text = output_textbox.get("1.0", tk.END).strip()
    pyperclip.copy(text)
    
    original_text = copy_button.cget("text")
    copy_button.configure(text="✅  Kopyalandı!", fg_color="#28a745")
    
    def reset_button():
        time.sleep(1.5)
        copy_button.configure(text=original_text, fg_color="#1f538d")
    
    threading.Thread(target=reset_button, daemon=True).start()

def clear_all():
    """Tüm alanları temizle"""
    css_textbox.delete("1.0", tk.END)
    html_textbox.delete("1.0", tk.END)
    js_textbox.delete("1.0", tk.END)
    css_textbox.insert("1.0", "<style>\n  /* CSS içerik buraya */\n</style>")
    html_textbox.insert("1.0", "<div>\n  <!-- HTML içerik buraya -->\n</div>")
    js_textbox.insert("1.0", "<script>\n  // JS içerik buraya\n</script>")
    on_any_input_change()

def toggle_theme():
    current_mode = ctk.get_appearance_mode()
    new_mode = "dark" if current_mode == "Light" else "light"
    ctk.set_appearance_mode(new_mode)
    theme_button.configure(text="Koyu Tema" if new_mode == "light" else "Açık Tema")
    logo_bg_frame.configure(fg_color="#7d7d7d" if new_mode == "dark" else "#fff")


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.iconbitmap(resource_path("assets/favicon.ico"))
app.geometry("1200x750")
app.resizable(True, True)
app.minsize(900, 600)
app.title("TrendTüccar Code to JSON Converter")

try:
    favicon_image = Image.open("assets/favicon.ico") 
    app.iconbitmap(resource_path("assets/favicon.ico"))
    
    # Linux/Mac için alternatif
    # app.iconphoto(True, tk.PhotoImage(file="favicon.ico"))
except:
    pass

header_frame = ctk.CTkFrame(app, height=80, corner_radius=0)
header_frame.pack(fill="x", padx=0, pady=0)
header_frame.pack_propagate(False)

logo_bg_frame = ctk.CTkFrame(header_frame, fg_color="#fff", corner_radius=10)
logo_bg_frame.pack(pady=10, padx=5)

try:
    logo_path = resource_path("assets/trendtuccar_logo.png")
    logo_image = Image.open(logo_path)
    logo_photo = CTkImage(light_image=logo_image, dark_image=logo_image, size=(288, 64))
    logo_label = ctk.CTkLabel(logo_bg_frame, image=logo_photo, text="")
    logo_label.pack(padx=15, pady=10)
except Exception as e:
    print(f"Logo yükleme hatası: {e}")  
    pass

controls_frame = ctk.CTkFrame(app, fg_color="transparent")
controls_frame.pack(fill="x", padx=20, pady=(10, 5))

button_container = ctk.CTkFrame(controls_frame, fg_color="transparent")
button_container.pack(side="right")

clear_button = ctk.CTkButton(button_container, text="Temizle", width=110, height=35,
                             command=clear_all, fg_color="#dc3545", hover_color="#c82333",
                             font=ctk.CTkFont(size=12))
clear_button.pack(side="right", padx=5)

theme_button = ctk.CTkButton(button_container, text="Koyu Tema", width=130, height=35,
                             command=toggle_theme, font=ctk.CTkFont(size=12))
theme_button.pack(side="right", padx=5)

main_container = ctk.CTkFrame(app, corner_radius=10)
main_container.pack(expand=True, fill="both", padx=15, pady=(5, 15))

scrollable_frame = ctk.CTkScrollableFrame(main_container, orientation="vertical")
scrollable_frame.pack(expand=True, fill="both", padx=5, pady=5)

content_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
content_frame.pack(expand=True, fill="both")

input_frame = ctk.CTkFrame(content_frame, corner_radius=10)
input_frame.pack(side="left", fill="both", expand=True, padx=(5, 2.5), pady=5)

input_title = ctk.CTkLabel(input_frame, text="Kod Girişi", 
                          font=ctk.CTkFont(size=16, weight="bold"))
input_title.pack(pady=(15, 10))

def create_labeled_textbox(frame, label_text, default_text, min_height=100):
    container = ctk.CTkFrame(frame, fg_color="transparent")
    container.pack(fill="both", expand=True, pady=5)
    
    header_frame = ctk.CTkFrame(container, height=30, fg_color="transparent")
    header_frame.pack(fill="x", pady=(0, 5))
    header_frame.pack_propagate(False)
    
    label = ctk.CTkLabel(header_frame, text=label_text, 
                        font=ctk.CTkFont(size=13, weight="bold"))
    label.pack(side="left", padx=5)
    
    status_label = ctk.CTkLabel(header_frame, text="○ Boş",
                               font=ctk.CTkFont(size=11), text_color="gray")
    status_label.pack(side="right", padx=5)
    
    textbox = ctk.CTkTextbox(container, height=min_height, font=("Consolas", 11), 
                            wrap="word", corner_radius=8, border_width=2)
    textbox.pack(fill="both", expand=True, padx=5)
    textbox.insert("1.0", default_text)
    
    def on_change(event=None):
        on_any_input_change()
    
    textbox.bind("<KeyRelease>", on_change)
    textbox.bind("<FocusOut>", on_change)
    
    return textbox, status_label

css_textbox, css_status_label = create_labeled_textbox(
    input_frame, "CSS", 
    "<style>\n  /* CSS içerik buraya */\n</style>", 120)

html_textbox, html_status_label = create_labeled_textbox(
    input_frame, "HTML", 
    "<div>\n  <!-- HTML içerik buraya -->\n</div>", 120)

js_textbox, js_status_label = create_labeled_textbox(
    input_frame, "JavaScript", 
    "<script>\n  // JS içerik buraya\n</script>", 120)

output_frame = ctk.CTkFrame(content_frame, corner_radius=10)
output_frame.pack(side="right", fill="both", expand=True, padx=(2.5, 5), pady=5)

output_header = ctk.CTkFrame(output_frame, height=50, fg_color="transparent")
output_header.pack(fill="x", pady=(15, 5))
output_header.pack_propagate(False)

output_title = ctk.CTkLabel(output_header, text="JSON Çıktısı", 
                           font=ctk.CTkFont(size=16, weight="bold"))
output_title.pack(side="left", padx=15)

char_count_label = ctk.CTkLabel(output_header, text="Toplam karakter: 0", 
                               font=ctk.CTkFont(size=11), text_color="gray")
char_count_label.pack(side="right", padx=15)

output_textbox = ctk.CTkTextbox(output_frame, wrap="word", font=("Courier New", 11),
                               corner_radius=8, border_width=2)
output_textbox.pack(expand=True, fill="both", pady=(0, 10), padx=15)
output_textbox.configure(state="disabled")

copy_button = ctk.CTkButton(output_frame, text="Panoya Kopyala", 
                           command=copy_to_clipboard, height=40, width=200,
                           font=ctk.CTkFont(size=13, weight="bold"))
copy_button.pack(pady=(0, 15))

status_frame = ctk.CTkFrame(app, height=25, corner_radius=0)
status_frame.pack(fill="x", side="bottom")
status_frame.pack_propagate(False)

status_label = ctk.CTkLabel(status_frame, text="Hazır - Kodlarınızı girin ve otomatik olarak JSON'a dönüştürülsün", 
                           font=ctk.CTkFont(size=10), text_color="gray")
status_label.pack(side="left", padx=10, pady=2)

version_label = ctk.CTkLabel(status_frame, text="v2.1", 
                            font=ctk.CTkFont(size=10), text_color="gray")
version_label.pack(side="right", padx=10, pady=2)

update_json_output()

app.mainloop()