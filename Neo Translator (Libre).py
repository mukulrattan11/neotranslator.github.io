import streamlit as st
import requests
from PIL import Image
import pytesseract

# Local translator fallback
from googletrans import Translator

# ------------------------------
# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\hp\New folder (2)\tesseract.exe"

# ------------------------------
# Page config
st.set_page_config(page_title="Neo Translator", layout="centered")

# ------------------------------
# Styles
st.markdown("""
<style>
.stApp {background: linear-gradient(to top, #000000, #4B0000); color: #ffffff;}
.stTextArea>div>div>textarea {
    background-color: rgba(255,255,255,0.1) !important;
    color: #000000 !important;
    border-radius: 10px;
    padding: 10px;
    font-size: 16px;
}



/* Make all labels white */
label { color: white !important; }




.stButton>button {
    background: linear-gradient(to top, rgba(102,0,0,0.3), rgba(100,0,0,0.95));
    color: #ffffff;
    border-radius: 10px;
    padding: 8px 16px;
}
.translated-box {
    background-color: rgba(255, 0, 0, 0.2);
    color: #FF0000;
    padding: 15px;
    border-radius: 10px;
    font-weight: bold;
    font-size: 18px;
    word-wrap: break-word;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------
# Title
st.title("🌏Neo Translator")

# ------------------------------
# Input method
input_method = st.selectbox("Choose input method:", ["Type/Paste Text", "Upload Image/Text File"])
text_to_translate = ""

if input_method == "Type/Paste Text":
    manual_text = st.text_area("Enter Your Text:")
    if manual_text and manual_text.strip():
        text_to_translate = manual_text.strip()
else:
    uploaded_file = st.file_uploader("Upload an image or text file", type=["png", "jpg", "jpeg", "txt"])
    if uploaded_file is not None:
        if uploaded_file.type == "text/plain":
            text_to_translate = uploaded_file.read().decode("utf-8")
        else:
            image = Image.open(uploaded_file)
            text_to_translate = pytesseract.image_to_string(image)
        st.text_area("Detected Text:", text_to_translate, height=150)

# ------------------------------
# Language selection
indian_languages = {
    "Assamese": "as", "Bengali": "bn", "Gujarati": "gu", "Hindi": "hi",
    "Kannada": "kn", "Malayalam": "ml", "Marathi": "mr", "Odia": "or",
    "Punjabi": "pa", "Tamil": "ta"
}
international_languages = {
    "Arabic": "ar", "Chinese": "zh-cn", "English": "en", "French": "fr",
    "German": "de", "Italian": "it", "Japanese": "ja", "Korean": "ko",
    "Portuguese": "pt", "Spanish": "es"
}

all_languages = {}
for name, code in sorted(indian_languages.items()):
    all_languages[f"Indian: {name}"] = code
for name, code in sorted(international_languages.items()):
    all_languages[f"International: {name}"] = code

selected_lang = st.selectbox("Select Translation Language:", ["None"] + list(all_languages.keys()))
target_lang = all_languages.get(selected_lang) if selected_lang != "None" else None

# ------------------------------
# Translate function with fallback
def translate_text(text: str, target: str) -> str:
    servers = [
        "https://translate.argosopentech.com/translate",
        "https://libretranslate.de/translate"
    ]
    payload = {"q": text, "source": "auto", "target": target, "format": "text"}
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    # Try LibreTranslate first
    for url in servers:
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if "translatedText" in data:
                    return data["translatedText"]
        except Exception:
            continue

    # Fallback: googletrans
    try:
        translator = Translator()
        result = translator.translate(text, dest=target)
        return result.text
    except Exception as e:
        return f"Translation failed: {e}"

# ------------------------------
# Translate button
if st.button("Translate"):
    if not text_to_translate:
        st.error("No text detected to translate.")
    elif not target_lang:
        st.error("Please select a language.")
    else:
        translated_text = translate_text(text_to_translate, target_lang)
        st.markdown(f"""
        <div class='translated-box'>
            Translation: {translated_text}
        </div>
        """, unsafe_allow_html=True)