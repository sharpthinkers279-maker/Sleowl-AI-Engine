import streamlit as st
import mysql.connector
from google import genai

# Professional Startup UI Config
st.set_page_config(page_title="Sleowl AI Engine", page_icon="🦉", layout="wide")

# Custom CSS for the Neon 'NextCalc' Vibe
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #00ffcc; }
    h1, h2, h3 { color: #00ffcc !important; font-family: 'Courier New'; }
    .stButton>button { 
        background: linear-gradient(45deg, #ff00ff, #00ffff); 
        color: white; border-radius: 15px; border: none; font-weight: bold;
    }
    </style>
    """, unsafe_style=True)

st.title("🦉 SLEOWL: BIO-KINETIC INTELLIGENCE")
st.sidebar.header("🔐 Secure Vault")

# Passwords remain in the sidebar to protect your startup's secrets
api_key = st.sidebar.text_input("Gemini API Key", type="password")
db_pass = st.sidebar.text_input("Aiven MySQL Password", type="password")

if not api_key or not db_pass:
    st.warning("Awaiting credentials to initialize the engine.")
    st.stop()

# --- Main App Logic ---
name = st.text_input("Client Name")
w = st.number_input("Weight (kg)", min_value=1.0)
h = st.number_input("Height (cm)", min_value=1.0)

if st.button("RUN AI DIAGNOSTIC"):
    bmi = round(w / ((h/100)**2), 2)
    client = genai.Client(api_key=api_key)
    
    # 2026 standard AI inference
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=f"As a Sleowl scientist, why does BMI {bmi} need specific alignment?"
    )
    
    st.success(f"BMI: {bmi}")
    st.info(f"**AI Doctor:** {response.text}")
    
    # Cloud Sync to Sleowl-ind
    conn = mysql.connector.connect(
        host='sleowl-ind-sleowl-db.k.aivencloud.com',
        user='avnadmin', password=db_pass, port='15618', database='defaultdb'
    )
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sleep_diagnostics (user_name, bmi) VALUES (%s, %s)", (name, bmi))
    conn.commit()
    conn.close()
