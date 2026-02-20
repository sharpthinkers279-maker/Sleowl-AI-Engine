import streamlit as st
import mysql.connector
from google import genai
import pandas as pd
from fpdf import FPDF
import datetime

# 1. PUBLIC UI CONFIG
st.set_page_config(page_title="Sleowl: Public Health Portal", page_icon="🦉", layout="wide")

# Neon Startup Branding
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #00ffcc; }
    h1, h2, h3 { color: #00ffcc !important; font-family: 'Courier New'; }
    .stButton>button { 
        background: linear-gradient(45deg, #ff00ff, #00ffff); 
        color: white; border-radius: 15px; border: none; font-weight: bold; width: 100%; height: 3.5em;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. PDF ENGINE FOR PUBLIC REPORTS
def create_report(user_name, plan, bmi):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 15, "Sleowl Clinical Diagnostic Report", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Patient Name: {user_name}", ln=True)
    pdf.cell(0, 10, f"Calculated BMI: {bmi}", ln=True)
    pdf.cell(0, 10, f"Date: {datetime.date.today()}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, plan)
    return pdf.output(dest='S').encode('latin-1')

# 3. SECURE SYSTEM ACCESS (Admin Only)
with st.sidebar:
    st.header("🔐 Sleowl Admin Vault")
    api_key = st.text_input("Gemini API Key", type="password")
    db_pass = st.text_input("Aiven MySQL Password", type="password")
    st.info("System credentials are required to serve public requests.")

if not api_key or not db_pass:
    st.warning("ENGINE OFFLINE: Admin must provide secure credentials to start diagnostics.")
    st.stop()

# 4. PUBLIC PORTAL
st.title("🧬 Sleowl: Advanced Bio-Intelligence Engine")
st.markdown("---")

col1, col2 = st.columns([3, 2], gap="large")

with col1:
    st.subheader("📋 Public Diagnostic Form")
    with st.container(border=True):
        name = st.text_input("Full Name / Identifier")
        c1, c2 = st.columns(2)
        with c1:
            w = st.number_input("Weight (kg)", min_value=1.0)
            ex = st.number_input("Exercise (Hours/Week)", min_value=0)
        with c2:
            h = st.number_input("Height (cm)", min_value=1.0)
            physical = st.selectbox("Current Physical State", ["Peak", "Normal", "Tired", "Injured"])
        
        mental = st.slider("Mental & Emotional Energy", 1, 10, 5)
        st.write("*(This helps us adjust your ergonomic and diet recommendations)*")

    if st.button("GENERATE MY PERSONALIZED HEALTH PLAN"):
        bmi = round(w / ((h/100)**2), 2)
        
        # 2026 AI Public Inference
        try:
            client = genai.Client(api_key=api_key)
            prompt = (f"User: {name}. BMI: {bmi}. Exercise: {ex} hrs/wk. State: {physical}. Mental: {mental}/10. "
                      f"Suggest a personalized VEGETARIAN diet and a 1-week recovery/exercise plan.")
            
            response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
            final_plan = response.text
            
            st.success("Prescription Ready for Download")
            st.markdown(final_plan)

            # SAVE TO SLEOWL BACK-END
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
            query = "INSERT INTO public_diagnostics (name, bmi, exercise_hrs, physical_state, mental_score, plan) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (name, bmi, ex, physical, mental, final_plan))
            conn.commit()
            conn.close()

            # PDF DOWNLOAD FOR THE PUBLIC
            report_bytes = create_report(name, final_plan, bmi)
            st.download_button(
                label="📥 DOWNLOAD MY SLEOWL REPORT (PDF)",
                data=report_bytes,
                file_name=f"Sleowl_Diagnostic_{name}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Engine Fault: {e}")

with col2:
    st.subheader("🌍 Sleowl Global Impact")
    st.write("Real-time telemetry from the diagnostic cloud.")
    # Here, we pull the average mental scores or BMI trends of the public users
    if st.checkbox("Show Public Health Trends"):
        try:
            conn = mysql.connector.connect(
                host='sleowl-ind-sleowl-db.k.aivencloud.com',
                user='avnadmin', password=db_pass, port='15618', database='defaultdb'
            )
            df = pd.read_sql("SELECT bmi, mental_score FROM public_diagnostics", conn)
            st.bar_chart(df['mental_score'])
            st.write(f"**Total Diagnostics Performed:** {len(df)}")
            conn.close()
        except:
            st.write("Database syncing...")
