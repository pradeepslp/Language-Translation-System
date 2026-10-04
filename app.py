"""
Language Translation System
A modern, simple, and responsive web application built using Python, Streamlit, and deep-translator.
Supports English, Tamil, Hindi, Spanish, French, German, and 25+ other languages.
"""

import socket
import urllib.request
import streamlit as st
from deep_translator import GoogleTranslator, MyMemoryTranslator
from deep_translator.exceptions import (
    LanguageNotSupportedException,
    NotValidPayload,
    TooManyRequests,
    TranslationNotFound,
)

# -----------------------------------------------------------------------------
# 1. Page Configuration & Custom CSS Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Language Translation System",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inject custom modern CSS
st.markdown(
    """
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main Header container */
    .header-box {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px 30px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }
    .header-title {
        color: #F8FAFC;
        font-size: 1.9rem;
        font-weight: 700;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .header-subtitle {
        color: #94A3B8;
        font-size: 0.95rem;
        margin-top: 6px;
        margin-bottom: 0;
    }
    .badge-pill {
        display: inline-block;
        background: rgba(59, 130, 246, 0.15);
        color: #60A5FA;
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 9999px;
        padding: 2px 10px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-top: 8px;
    }

    /* Translation Card Containers */
    .card-label {
        font-weight: 600;
        font-size: 0.95rem;
        color: #334155;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    @media (prefers-color-scheme: dark) {
        .card-label {
            color: #E2E8F0;
        }
    }

    .output-card {
        background: #F8FAFC;
        border: 1.5px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px;
        min-height: 180px;
        font-size: 1rem;
        color: #0F172A;
        white-space: pre-wrap;
        word-break: break-word;
        line-height: 1.6;
    }

    @media (prefers-color-scheme: dark) {
        .output-card {
            background: #1E293B;
            border-color: #334155;
            color: #F1F5F9;
        }
    }

    .output-placeholder {
        color: #94A3B8;
        font-style: italic;
    }

    /* Status & Meta info */
    .meta-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 8px;
        font-size: 0.8rem;
        color: #64748B;
    }

    /* Example pill buttons container */
    .sample-pill-title {
        font-size: 0.85rem;
        color: #64748B;
        margin-bottom: 6px;
        font-weight: 500;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 2. Supported Languages Definition & Mappings
# -----------------------------------------------------------------------------
# Comprehensive dictionary of supported languages mapped to standard codes
# Compatible with both GoogleTranslator and MyMemoryTranslator backends
LANGUAGE_CATALOG = {
    "English": {"code": "en", "google": "en", "mymemory": "en-GB"},
    "Tamil (தமிழ்)": {"code": "ta", "google": "ta", "mymemory": "ta-IN"},
    "Hindi (हिन्दी)": {"code": "hi", "google": "hi", "mymemory": "hi-IN"},
    "Spanish (Español)": {"code": "es", "google": "es", "mymemory": "es-ES"},
    "French (Français)": {"code": "fr", "google": "fr", "mymemory": "fr-FR"},
    "German (Deutsch)": {"code": "de", "google": "de", "mymemory": "de-DE"},
    "Telugu (తెలుగు)": {"code": "te", "google": "te", "mymemory": "te-IN"},
    "Malayalam (മലയാളം)": {"code": "ml", "google": "ml", "mymemory": "ml-IN"},
    "Kannada (ಕನ್ನಡ)": {"code": "kn", "google": "kn", "mymemory": "kn-IN"},
    "Bengali (বাংলা)": {"code": "bn", "google": "bn", "mymemory": "bn-IN"},
    "Gujarati (ગુજરાતી)": {"code": "gu", "google": "gu", "mymemory": "gu-IN"},
    "Marathi (मराठी)": {"code": "mr", "google": "mr", "mymemory": "mr-IN"},
    "Punjabi (ਪੰਜਾਬੀ)": {"code": "pa", "google": "pa", "mymemory": "pa-IN"},
    "Urdu (اردو)": {"code": "ur", "google": "ur", "mymemory": "ur-PK"},
    "Arabic (العربية)": {"code": "ar", "google": "ar", "mymemory": "ar-SA"},
    "Chinese Simplified (简体中文)": {"code": "zh-CN", "google": "zh-CN", "mymemory": "zh-CN"},
    "Chinese Traditional (繁體中文)": {"code": "zh-TW", "google": "zh-TW", "mymemory": "zh-TW"},
    "Japanese (日本語)": {"code": "ja", "google": "ja", "mymemory": "ja-JP"},
    "Korean (한국어)": {"code": "ko", "google": "ko", "mymemory": "ko-KR"},
    "Russian (Русский)": {"code": "ru", "google": "ru", "mymemory": "ru-RU"},
    "Portuguese (Português)": {"code": "pt", "google": "pt", "mymemory": "pt-PT"},
    "Italian (Italiano)": {"code": "it", "google": "it", "mymemory": "it-IT"},
    "Dutch (Nederlands)": {"code": "nl", "google": "nl", "mymemory": "nl-NL"},
    "Turkish (Türkçe)": {"code": "tr", "google": "tr", "mymemory": "tr-TR"},
    "Vietnamese (Tiếng Việt)": {"code": "vi", "google": "vi", "mymemory": "vi-VN"},
    "Indonesian (Bahasa Indonesia)": {"code": "id", "google": "id", "mymemory": "id-ID"},
    "Greek (Ελληνικά)": {"code": "el", "google": "el", "mymemory": "el-GR"},
    "Polish (Polski)": {"code": "pl", "google": "pl", "mymemory": "pl-PL"},
    "Swedish (Svenska)": {"code": "sv", "google": "sv", "mymemory": "sv-SE"},
    "Thai (ไทย)": {"code": "th", "google": "th", "mymemory": "th-TH"},
}

SOURCE_LANGUAGE_OPTIONS = ["Auto Detect"] + list(LANGUAGE_CATALOG.keys())
TARGET_LANGUAGE_OPTIONS = list(LANGUAGE_CATALOG.keys())

# Example sentences for quick user testing
SAMPLE_SENTENCES = [
    ("Hello, how are you?", "English", "Tamil (தமிழ்)"),
    ("Welcome to the Language Translation System.", "English", "Tamil (தமிழ்)"),
    ("வணக்கம், இன்றைய நாள் இனிய நாளாக அமையட்டும்!", "Tamil (தமிழ்)", "English"),
    ("Artificial intelligence is transforming our world.", "English", "Hindi (हिन्दी)"),
    ("Have a wonderful day!", "English", "French (Français)"),
]

# -----------------------------------------------------------------------------
# 3. Helper Functions & Connectivity Checks
# -----------------------------------------------------------------------------
def check_internet_connection(host: str = "8.8.8.8", port: int = 53, timeout: float = 3.0) -> bool:
    """
    Checks if active internet connection is available.
    Uses socket connection to DNS resolver for fast and reliable network check.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except (socket.timeout, socket.error, OSError):
        # Secondary fallback check via HTTP
        try:
            urllib.request.urlopen("https://www.google.com", timeout=timeout)
            return True
        except Exception:
            return False


def perform_translation(text: str, source_display: str, target_display: str) -> tuple[str, str]:
    """
    Translates text using deep-translator with resilient fallback architecture.
    Returns (translated_text, engine_used_name).
    """
    # Validate source and target inputs
    target_info = LANGUAGE_CATALOG.get(target_display)
    if not target_info:
        raise LanguageNotSupportedException(f"Unsupported target language: {target_display}")

    if source_display == "Auto Detect":
        source_google = "auto"
        source_mymemory = "auto"
    else:
        source_info = LANGUAGE_CATALOG.get(source_display)
        if not source_info:
            raise LanguageNotSupportedException(f"Unsupported source language: {source_display}")
        source_google = source_info["google"]
        source_mymemory = source_info["mymemory"]

    target_google = target_info["google"]
    target_mymemory = target_info["mymemory"]

    # 1. First Attempt: GoogleTranslator via deep-translator
    try:
        translator = GoogleTranslator(source=source_google, target=target_google)
        result = translator.translate(text)
        if result and result.strip():
            return result, "Google Translator (deep-translator)"
    except (TooManyRequests, Exception) as g_err:
        # If rate limit, 429, or temporary issue occurs, proceed to MyMemoryTranslator fallback
        pass

    # 2. Resilient Fallback: MyMemoryTranslator via deep-translator
    try:
        # MyMemory works best with country-mapped codes or 'auto'
        src_param = "auto" if source_display == "Auto Detect" else source_mymemory
        translator_mm = MyMemoryTranslator(source=src_param, target=target_mymemory)
        result_mm = translator_mm.translate(text)
        if result_mm and result_mm.strip():
            return result_mm, "MyMemory Translator (deep-translator)"
    except Exception as mm_err:
        raise RuntimeError(
            f"Translation service is temporarily unreachable. Please check your internet connection or try again shortly."
        )

    raise RuntimeError("Unable to translate text at this time. Please try again.")


# -----------------------------------------------------------------------------
# 4. Session State Initialization
# -----------------------------------------------------------------------------
if "input_text" not in st.session_state:
    st.session_state.input_text = ""
if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""
if "source_lang" not in st.session_state:
    st.session_state.source_lang = "English"
if "target_lang" not in st.session_state:
    st.session_state.target_lang = "Tamil (தமிழ்)"
if "engine_used" not in st.session_state:
    st.session_state.engine_used = ""
if "status_message" not in st.session_state:
    st.session_state.status_message = None


# Callback functions for buttons
def clear_all_fields():
    """Clears all input, output, and status state."""
    st.session_state.input_text = ""
    st.session_state.translated_text = ""
    st.session_state.engine_used = ""
    st.session_state.status_message = None


def swap_selected_languages():
    """Swaps source and target languages if source is not Auto Detect."""
    current_src = st.session_state.source_lang
    current_tgt = st.session_state.target_lang

    if current_src == "Auto Detect":
        st.session_state.status_message = {
            "type": "warning",
            "text": "Cannot swap when Source Language is set to 'Auto Detect'. Please choose a specific source language.",
        }
        return

    # Swap
    st.session_state.source_lang = current_tgt
    st.session_state.target_lang = current_src

    # Also swap texts if both exist
    if st.session_state.translated_text:
        old_input = st.session_state.input_text
        st.session_state.input_text = st.session_state.translated_text
        st.session_state.translated_text = old_input
    st.session_state.status_message = None


def set_sample_sentence(sample_text: str, src: str, tgt: str):
    """Populates input and selects language from sample click."""
    st.session_state.input_text = sample_text
    st.session_state.source_lang = src
    st.session_state.target_lang = tgt
    st.session_state.translated_text = ""
    st.session_state.engine_used = ""
    st.session_state.status_message = None


# -----------------------------------------------------------------------------
# 5. Header Section
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="header-box">
        <h1 class="header-title">
            <span>🌐</span> Language Translation System
        </h1>
        <p class="header-subtitle">
            Instantly translate text across 30+ languages including English, Tamil, Hindi, French, Spanish, and more.
        </p>
        <span class="badge-pill">⚡ Powered by deep-translator (Free & Open Source)</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 6. Quick Sample Sentence Selection
# -----------------------------------------------------------------------------
st.markdown('<p class="sample-pill-title">💡 <strong>Quick Examples:</strong> Click any phrase to test quickly</p>', unsafe_allow_html=True)
sample_cols = st.columns(len(SAMPLE_SENTENCES))
for idx, (sample_txt, s_lang, t_lang) in enumerate(SAMPLE_SENTENCES):
    with sample_cols[idx]:
        btn_label = sample_txt if len(sample_txt) <= 24 else f"{sample_txt[:22]}..."
        if st.button(btn_label, key=f"sample_{idx}", use_container_width=True, help=f"{sample_txt} ({s_lang} ➔ {t_lang})"):
            set_sample_sentence(sample_txt, s_lang, t_lang)
            st.rerun()

st.write("")

# -----------------------------------------------------------------------------
# 7. Language Selection Bar
# -----------------------------------------------------------------------------
col_src, col_swap, col_tgt = st.columns([10, 2, 10])

with col_src:
    src_idx = (
        SOURCE_LANGUAGE_OPTIONS.index(st.session_state.source_lang)
        if st.session_state.source_lang in SOURCE_LANGUAGE_OPTIONS
        else 0
    )
    source_language = st.selectbox(
        "Source Language",
        options=SOURCE_LANGUAGE_OPTIONS,
        index=src_idx,
        key="source_select",
        help="Select the language of your input text or choose Auto Detect.",
    )
    st.session_state.source_lang = source_language

with col_swap:
    st.write("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    st.button(
        "⇄ Swap",
        key="swap_btn",
        on_click=swap_selected_languages,
        help="Swap Source and Target languages",
        use_container_width=True,
    )

with col_tgt:
    tgt_idx = (
        TARGET_LANGUAGE_OPTIONS.index(st.session_state.target_lang)
        if st.session_state.target_lang in TARGET_LANGUAGE_OPTIONS
        else 1  # Default to Tamil
    )
    target_language = st.selectbox(
        "Target Language",
        options=TARGET_LANGUAGE_OPTIONS,
        index=tgt_idx,
        key="target_select",
        help="Select the target language for translation.",
    )
    st.session_state.target_lang = target_language

# -----------------------------------------------------------------------------
# 8. Input & Output Text Area Columns
# -----------------------------------------------------------------------------
col_input, col_output = st.columns(2)

with col_input:
    st.markdown(
        f'<div class="card-label"><span>📝 Input Text ({st.session_state.source_lang})</span></div>',
        unsafe_allow_html=True,
    )
    input_text = st.text_area(
        label="Input Text",
        value=st.session_state.input_text,
        height=220,
        placeholder="Type or paste text here to translate...",
        key="input_text_area",
        label_visibility="collapsed",
    )
    # Sync session state with text area input
    st.session_state.input_text = input_text

    char_count = len(st.session_state.input_text)
    word_count = len(st.session_state.input_text.split()) if st.session_state.input_text.strip() else 0
    st.markdown(
        f'<div class="meta-bar"><span>Characters: {char_count} | Words: {word_count}</span></div>',
        unsafe_allow_html=True,
    )

with col_output:
    st.markdown(
        f'<div class="card-label"><span>✨ Translated Output ({st.session_state.target_lang})</span></div>',
        unsafe_allow_html=True,
    )

    if st.session_state.translated_text:
        st.markdown(
            f'<div class="output-card">{st.session_state.translated_text}</div>',
            unsafe_allow_html=True,
        )
        out_chars = len(st.session_state.translated_text)
        out_words = len(st.session_state.translated_text.split())
        engine_label = f"• {st.session_state.engine_used}" if st.session_state.engine_used else ""
        st.markdown(
            f'<div class="meta-bar"><span>Characters: {out_chars} | Words: {out_words}</span><span>{engine_label}</span></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="output-card output-placeholder">The translation will appear here after clicking "Translate"...</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="meta-bar"><span>Ready for translation</span></div>',
            unsafe_allow_html=True,
        )

# -----------------------------------------------------------------------------
# 9. Control Buttons (Translate & Clear)
# -----------------------------------------------------------------------------
st.write("")
btn_col1, btn_col2, btn_col3 = st.columns([3, 2, 5])

with btn_col1:
    translate_clicked = st.button("🚀 Translate", type="primary", use_container_width=True)

with btn_col2:
    st.button("🗑️ Clear All", on_click=clear_all_fields, use_container_width=True)

with btn_col3:
    if st.session_state.translated_text:
        st.download_button(
            label="📥 Download Translation (.txt)",
            data=st.session_state.translated_text,
            file_name="translated_text.txt",
            mime="text/plain",
            use_container_width=True,
        )

# -----------------------------------------------------------------------------
# 10. Translation Execution & Error Handling
# -----------------------------------------------------------------------------
if translate_clicked:
    cleaned_input = st.session_state.input_text.strip()

    # Case 1: Empty or whitespace input
    if not cleaned_input:
        st.session_state.status_message = {
            "type": "warning",
            "text": "⚠️ Please enter some text in the input box to translate.",
        }
        st.session_state.translated_text = ""
        st.session_state.engine_used = ""

    # Case 2: Same Source and Target language
    elif (
        st.session_state.source_lang != "Auto Detect"
        and st.session_state.source_lang == st.session_state.target_lang
    ):
        st.session_state.status_message = {
            "type": "info",
            "text": "ℹ️ Source and Target languages are identical. Input text copied directly.",
        }
        st.session_state.translated_text = cleaned_input
        st.session_state.engine_used = "Direct Match"

    # Case 3: Perform Translation
    else:
        # Check internet connection first
        with st.spinner("Translating text... Please wait"):
            is_connected = check_internet_connection()

            if not is_connected:
                st.session_state.status_message = {
                    "type": "error",
                    "text": "❌ Internet Connection Error: Please verify your internet connection and try again.",
                }
            else:
                try:
                    result, engine = perform_translation(
                        cleaned_input,
                        st.session_state.source_lang,
                        st.session_state.target_lang,
                    )
                    st.session_state.translated_text = result
                    st.session_state.engine_used = engine
                    st.session_state.status_message = {
                        "type": "success",
                        "text": f"✅ Translated successfully using {engine}!",
                    }
                except LanguageNotSupportedException as lang_err:
                    st.session_state.status_message = {
                        "type": "error",
                        "text": f"⚠️ Unsupported Language: {str(lang_err)}",
                    }
                except NotValidPayload:
                    st.session_state.status_message = {
                        "type": "error",
                        "text": "⚠️ Invalid input text format. Please enter valid text characters.",
                    }
                except TranslationNotFound:
                    st.session_state.status_message = {
                        "type": "error",
                        "text": "⚠️ No translation found for the given input phrase.",
                    }
                except Exception as ex:
                    st.session_state.status_message = {
                        "type": "error",
                        "text": f"❌ Translation Error: {str(ex)}",
                    }

    st.rerun()

# -----------------------------------------------------------------------------
# 11. Display Status & Alerts
# -----------------------------------------------------------------------------
if st.session_state.status_message:
    msg_type = st.session_state.status_message.get("type")
    msg_text = st.session_state.status_message.get("text")

    if msg_type == "success":
        st.success(msg_text)
    elif msg_type == "warning":
        st.warning(msg_text)
    elif msg_type == "info":
        st.info(msg_text)
    elif msg_type == "error":
        st.error(msg_text)

# -----------------------------------------------------------------------------
# 12. Footer Information
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #94A3B8; font-size: 0.85rem; padding: 10px 0;">
        <strong>Language Translation System</strong> • Built with Python & Streamlit • No API key required
    </div>
    """,
    unsafe_allow_html=True,
)
