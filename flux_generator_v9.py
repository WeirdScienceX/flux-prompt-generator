import streamlit as st
from google import genai
from google.genai import types
import json
import re
import pandas as pd
import datetime
import os # <--- Added to check for file existence

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Flux 2 Studio", page_icon="⚡", layout="wide")
HISTORY_FILE = "prompt_history.json" # <--- The file where we store memory

# --- 2. CSS STYLING (Unchanged) ---
def local_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
        html, body, [class*="css"] { font-family: 'JetBrains Mono', monospace; }
        h1 { background: -webkit-linear-gradient(45deg, #00FF94, #00B8FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700 !important; }
        .stTextInput > div > div > input { background-color: #262730; color: #00FF94; border-radius: 10px; border: 1px solid #4A4A4A; }
        .prompt-card { background-color: #1E1E1E; border-left: 5px solid #00FF94; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .negative-card { background-color: #1E1E1E; border-left: 5px solid #FF4B4B; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        div.stButton > button { background: linear-gradient(45deg, #00FF94, #00B8FF); color: black; border: none; border-radius: 8px; font-weight: bold; transition: transform 0.2s; }
        div.stButton > button:hover { transform: scale(1.02); color: black; }
    </style>
    """, unsafe_allow_html=True)
local_css()

# --- 3. PERSISTENCE FUNCTIONS (NEW) ---
def load_prompt_history():
    """Loads the list of prompts from the JSON file on disk."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except:
            return [] # If file is corrupt, return empty list
    return []

def save_prompt_history(prompt_list):
    """Saves the current list to disk."""
    with open(HISTORY_FILE, "w") as f:
        json.dump(prompt_list, f)

# --- 4. AUTHENTICATION ---
def check_password():
    if st.secrets.get("IS_LOCAL", False): return True
    if "APP_PASSWORD" not in st.secrets: st.stop() 
    def password_entered():
        if st.session_state["password"] == st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else: st.session_state["password_correct"] = False
    if st.session_state.get("password_correct", False): return True
    st.text_input("Enter Password:", type="password", on_change=password_entered, key="password")
    return False

if not check_password(): st.stop()

# --- 5. SETUP & STATE ---
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except: st.stop()

if "history" not in st.session_state: st.session_state.history = []
if "last_result" not in st.session_state: st.session_state.last_result = None

# LOAD FROM DISK ON STARTUP
if "prompt_list" not in st.session_state:
    st.session_state.prompt_list = load_prompt_history()

if "input_idea" not in st.session_state: st.session_state.input_idea = ""
if "input_style" not in st.session_state: st.session_state.input_style = "Photorealistic"
if "input_ratio" not in st.session_state: st.session_state.input_ratio = "Cinematic (16:9)"

def restore_state(item):
    st.session_state.input_idea = item['idea']
    st.session_state.input_style = item.get('style', "Photorealistic") 
    st.session_state.input_ratio = item.get('ratio', "Cinematic (16:9)")
    st.session_state.last_result = {
        "positive_prompt": item['positive'],
        "negative_prompt": item['negative'],
        "explanation": item.get('explanation', '')
    }
def load_from_dropdown():
    if st.session_state.recent_selected:
        st.session_state.input_idea = st.session_state.recent_selected

# --- 6. LOGIC ---
def generate_flux_data(user_idea, style_mode, ratio, selected_model):
    prompt_logic = f"""
    Act as an expert Prompt Engineer for FLUX.1.
    RULE: Use NATURAL LANGUAGE. No tag soup.
    INPUT: "{user_idea}" | STYLE: {style_mode} | RATIO: {ratio}
    OUTPUT JSON: {{ "positive_prompt": "...", "negative_prompt": "...", "explanation": "..." }}
    """
    try:
        response = client.models.generate_content(
            model=selected_model, contents=prompt_logic,
            config=types.GenerateContentConfig(temperature=0.7, response_mime_type="application/json")
        )
        return response.text
    except Exception as e: return f'{{"error": "{str(e)}"}}'

def parse_response(txt):
    try: return json.loads(re.sub(r'```json\s*|```', '', txt).strip())
    except: return {"positive_prompt": txt, "negative_prompt": "Error", "explanation": "Error"}

# --- 7. FRONTEND ---
with st.sidebar:
    st.header("🧠 Engine")
    model_choice = st.radio("Model:", ["gemini-flash-latest", "gemini-pro-latest"], captions=["Fast", "Creative"], label_visibility="collapsed")
    st.divider()
    st.header("📜 History")
    if len(st.session_state.history) > 0:
        df = pd.DataFrame(st.session_state.history)
        st.download_button("📥 Export CSV", df.to_csv(index=False).encode('utf-8'), "prompts.csv", "text/csv")
    
    # CLEAR BUTTON NOW WIPES FILE TOO
    if st.button("🗑️ Clear Memory"):
        st.session_state.history = []
        st.session_state.prompt_list = []
        st.session_state.last_result = None
        save_prompt_history([]) # <--- Wipe disk
        st.rerun()
        
    st.markdown("---")
    for i, item in enumerate(reversed(st.session_state.history)):
        with st.expander(f"{item['timestamp']} - {item['idea'][:15]}..."):
            st.button("⬆️ Load", key=f"r_{i}", on_click=restore_state, args=(item,))

# MAIN UI
st.title("⚡ Flux 2 Studio")

col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    if len(st.session_state.prompt_list) > 0:
        st.selectbox("Recent:", st.session_state.prompt_list, index=None, placeholder="Quick Load...", key="recent_selected", on_change=load_from_dropdown, label_visibility="collapsed")
    st.text_input("Core Concept:", key="input_idea", placeholder="Describe your imagination...")
with col2:
    st.selectbox("Style", ["Photorealistic", "Digital Art/3D", "Anime/Manga", "Typography"], key="input_style")
with col3:
    st.selectbox("Ratio", ["Square (1:1)", "Cinematic (16:9)", "Vertical (9:16)"], key="input_ratio")

if st.button("✨ Generate Prompt", type="primary"):
    if not st.session_state.input_idea: st.warning("Enter a concept first!")
    else:
        with st.spinner("Engineering..."):
            data = parse_response(generate_flux_data(st.session_state.input_idea, st.session_state.input_style, st.session_state.input_ratio, model_choice))
            
            # --- PERSISTENCE LOGIC START ---
            # 1. Update List
            if st.session_state.input_idea in st.session_state.prompt_list: 
                st.session_state.prompt_list.remove(st.session_state.input_idea)
            st.session_state.prompt_list.insert(0, st.session_state.input_idea)
            st.session_state.prompt_list = st.session_state.prompt_list[:25]
            
            # 2. SAVE TO DISK IMMEDIATELY
            save_prompt_history(st.session_state.prompt_list)
            # --- PERSISTENCE LOGIC END ---

            st.session_state.history.append({
                "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                "idea": st.session_state.input_idea,
                "style": st.session_state.input_style,
                "ratio": st.session_state.input_ratio,
                "model": model_choice,
                **data
            })
            st.session_state.last_result = data
            st.rerun()

# --- DISPLAY ---
if st.session_state.last_result:
    res = st.session_state.last_result
    st.divider()
    st.markdown(f"""
    <div class="prompt-card">
        <h4 style="margin:0; color:#00FF94;">POSITIVE PROMPT</h4>
        <p style="font-size:1.1em; color: white;">{res.get("positive_prompt")}</p>
    </div>
    <div class="negative-card">
        <h4 style="margin:0; color:#FF4B4B;">NEGATIVE PROMPT</h4>
        <p style="color: #cccccc; font-size: 0.9em;">{res.get("negative_prompt")}</p>
    </div>
    """, unsafe_allow_html=True)
    with st.expander("💡 Logic Explanation", expanded=False):
        st.write(res.get("explanation"))