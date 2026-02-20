import streamlit as st
import mysql.connector
from google import genai
import pandas as pd

# 1. ENTERPRISE UI CONFIG
st.set_page_config(page_title="Sleowl Health Ecosystem", page_icon="🦉", layout="wide")

# Custom CSS: Neon Style
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #00ffcc; }
    h1, h2, h3 { color: #00ffcc !important; font-family: 'Courier New'; }
    .stButton>button { 
        background: linear-gradient(45deg, #ff00ff, #00ffff); 
        color: white; border-radius: 15px; border: none; font-weight: bold; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. SECURE SIDEBAR
with st.sidebar:
    st.header("🔐 Secure Access")
    api_key = st.text_input("Gemini API Key", type="password")
    db_pass = st.text_input("Aiven MySQL Password", type="password")

if not api_key or not db_pass:
    st.warning("Enter credentials to wake the Sleowl engine.")
    st.stop()

# 3. NAVIGATION TABS
tab1, tab2 = st.tabs(["🚀 Diagnostic Engine", "📂 Management Portal"])

with tab1:
    st.title("🧬 Sleowl Bio-Intelligence")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 Personal Vitals")
        name = st.text_input("Full Name")
        w = st.number_input("Weight (kg)", min_value=1.0)
        h = st.number_input("Height (cm)", min_value=1.0)
        ex = st.number_input("Exercise (Hours/Week)", min_value=0)
        
    with col2:
        st.subheader("🧠 Holistic Status")
        physical = st.selectbox("Physical State", ["Peak Performance", "Standard", "Fatigued", "Injured"])
        mental = st.slider("Mental Energy Level", 1, 10, 5)
        notes = st.text_area("How are you feeling today?")

    if st.button("GENERATE AI HEALTH PRESCRIPTION"):
        bmi = round(w / ((h/100)**2), 2)
        
        # 2026 AI LIFESTYLE ENGINE
        try:
            client = genai.Client(api_key=api_key)
            # Notice the 'Vegetarian' constraint included for accuracy
            prompt = (f"User BMI: {bmi}. Exercise: {ex} hrs/wk. State: {physical}. Mental Energy: {mental}/10. "
                      f"Context: {notes}. Suggest a strict VEGETARIAN diet and 1-week exercise plan for peak Pilot performance.")
            
            response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
            plan = response.text
            
            st.success("Sleowl Prescription Generated")
            st.markdown(f"### 🥦 AI Suggested Plan\n{plan}")

            # SYNC TO AIVEN CLOUD
            conn = mysql.connector.connect(
                host='sleowl-ind-sleowl-db.k.aivencloud.com',
                user='avnadmin', password=db_pass, port='15618', database='defaultdb'
            )
            cursor = conn.cursor()
            # Creating table if it doesn't exist for the new features
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sleowl_vitals (
                    id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100), bmi FLOAT, 
                    exercise_hrs INT, p_state VARCHAR(50), m_score INT, prescription TEXT
                )
            """)
            query = "INSERT INTO sleowl_vitals (name, bmi, exercise_hrs, p_state, m_score, prescription) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (name, bmi, ex, physical, mental, plan))
            conn.commit()
            conn.close()
            st.toast("Back-end Sync Successful.")
        except Exception as e:
            st.error(f"System Fault: {e}")

with tab2:
    st.title("📊 Enterprise Back-End")
    if st.button("REFRESH DATABASE"):
        try:
            conn = mysql.connector.connect(
                host='sleowl-ind-sleowl-db.k.aivencloud.com',
                user='avnadmin', password=db_pass, port='15618', database='defaultdb'
            )
            df = pd.read_sql("SELECT name, bmi, exercise_hrs, p_state, m_score FROM sleowl_vitals", conn)
            st.dataframe(df, use_container_width=True) # Professional data view
            conn.close()
        except Exception as e:
            st.error(f"Access Denied: {e}")
