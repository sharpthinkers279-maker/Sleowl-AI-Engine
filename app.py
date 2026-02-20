import streamlit as st
import mysql.connector
from google import genai
import pandas as pd
from fpdf import FPDF
import datetime

# 1. PLATFORM CONFIGURATION
st.set_page_config(page_title="Sleowl AI Engine", page_icon="🦉", layout="wide")

# Custom Neon CSS with Credit Styling
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #00ffcc; }
    h1, h2, h3 { color: #00ffcc !important; font-family: 'Courier New'; }
    .stButton>button { 
        background: linear-gradient(45deg, #ff00ff, #00ffff); 
        color: white; border-radius: 12px; border: none; font-weight: bold; height: 3.5em;
    }
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #1a1c24; color: #00ffcc; text-align: center;
        padding: 10px; font-family: 'Courier New'; font-size: 14px;
        border-top: 1px solid #ff00ff;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. LEGAL GATEWAY
if 'tos_agreed' not in st.session_state:
    st.session_state.tos_agreed = False

if not st.session_state.tos_agreed:
    st.title("⚖️ Sleowl User Agreement")
    st.warning("Please review our terms to initialize the AI engine.")
    st.write("1. **Not Medical Advice**: Suggestions are AI-generated based on morphology.")
    st.write("2. **Data Policy**: Metrics are synced to Sleowl's Aiven Cloud for analysis.")
    if st.button("I AGREE & PROCEED"):
        st.session_state.tos_agreed = True
        st.rerun()
    st.stop()

# 3. SECURE ADMIN ACCESS
with st.sidebar:
    st.header("🔐 Admin Vault")
    api_key = st.text_input("Gemini API Key", type="password")
    db_pass = st.text_input("Aiven MySQL Password", type="password")

if not api_key or not db_pass:
    st.error("AUTHENTICATION REQUIRED: Please contact the administrator.")
    st.stop()

# 4. MAIN ENGINE INTERFACE
st.title("🦉 SLEOWL: BIO-KINETIC INTELLIGENCE")
st.markdown("---")

col1, col2 = st.columns([3, 2], gap="large")

with col1:
    st.subheader("📋 Diagnostic Entry")
    with st.form("diagnostic_form"):
        name = st.text_input("Patient Full Name")
        c1, c2 = st.columns(2)
        with c1:
            w = st.number_input("Weight (kg)", min_value=1.0)
            ex = st.number_input("Weekly Exercise (Hrs)", min_value=0)
        with c2:
            h = st.number_input("Height (cm)", min_value=1.0)
            state = st.selectbox("Physical Status", ["Peak", "Normal", "Fatigued", "Injured"])
        
        mental = st.slider("Mental Energy Score", 1, 10, 5)
        notes = st.text_area("Health & Goal Context")
        submitted = st.form_submit_button("GENERATE SLEOWL PRESCRIPTION")

    if submitted:
        bmi = round(w / ((h/100)**2), 2)
        try:
            # 2026 AI Initialization
            client = genai.Client(api_key=api_key)
            prompt = (f"Analyze for {name}: BMI {bmi}, {ex} hrs exercise, {state} state, {mental}/10 mental energy. "
                      f"Context: {notes}. Suggest a VEGETARIAN diet and recovery plan.")
            
            response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
            plan = response.text
            
            st.success("Prescription Generated Successfully")
            st.markdown(plan)

            # Cloud Sync to Sleowl-ind
            conn = mysql.connector.connect(
                host='sleowl-ind-sleowl-db.k.aivencloud.com',
                user='avnadmin', password=db_pass, port='15618', database='defaultdb'
            )
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS public_diagnostics (
                    id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100), bmi FLOAT, 
                    exercise_hrs INT, physical_state VARCHAR(50), mental_score INT, plan TEXT
                )
            """)
            cursor.execute("INSERT INTO public_diagnostics (name, bmi, exercise_hrs, physical_state, mental_score, plan) VALUES (%s, %s, %s, %s, %s, %s)", 
                           (name, bmi, ex, state, mental, plan))
            conn.commit()
            conn.close()
            st.toast("Telemetry saved to Cloud Database")
        except Exception as e:
            st.error(f"Engine Fault: {e}")

with col2:
    st.subheader("🌍 Global Telemetry")
    if st.checkbox("Show Real-time Analytics"):
        try:
            conn = mysql.connector.connect(host='sleowl-ind-sleowl-db.k.aivencloud.com', user='avnadmin', password=db_pass, port='15618', database='defaultdb')
            df = pd.read_sql("SELECT bmi, mental_score FROM public_diagnostics", conn)
            st.metric("Total Diagnostics Served", len(df))
            st.line_chart(df['mental_score'])
            conn.close()
        except:
            st.info("Synchronizing with Aiven Cloud...")

# 5. THE AUTHOR FOOTER
st.markdown("""
    <div class="footer">
        <p>Built with ❤️ by Devansh Nadpara | Powered by Sleowl AI Engine 🦉</p>
    </div>
    """, unsafe_allow_html=True)
