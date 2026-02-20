import streamlit as st
import mysql.connector
from google import genai
import pandas as pd
from fpdf import FPDF
import datetime

# 1. ENTERPRISE CONFIG & UI
st.set_page_config(page_title="Sleowl AI Engine", page_icon="🦉", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #00ffcc; }
    h1, h2, h3 { color: #00ffcc !important; font-family: 'Courier New'; }
    .stButton>button { 
        background: linear-gradient(45deg, #ff00ff, #00ffff); 
        color: white; border-radius: 12px; border: none; font-weight: bold; height: 3.5em; width: 100%;
    }
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #1a1c24; color: #00ffcc; text-align: center;
        padding: 10px; font-family: 'Courier New'; font-size: 14px;
        border-top: 1px solid #ff00ff;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. PDF ENGINE
def create_report(user_name, plan, bmi):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 15, "Sleowl Clinical Diagnostic Report", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Patient Name: {user_name}", ln=True)
    pdf.cell(0, 10, f"Calculated BMI: {bmi}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, plan)
    return pdf.output(dest='S').encode('latin-1')

# 3. LEGAL & ADMIN GATEWAY
if 'tos_agreed' not in st.session_state:
    st.session_state.tos_agreed = False

if not st.session_state.tos_agreed:
    st.title("⚖️ Sleowl User Agreement")
    st.write("By using this AI engine, you agree that suggestions are for diagnostic simulation only.")
    if st.button("I AGREE & PROCEED"):
        st.session_state.tos_agreed = True
        st.rerun()
    st.stop()

with st.sidebar:
    st.header("🔐 Admin Vault")
    api_key = st.sidebar.text_input("Gemini API Key", type="password")
    db_pass = st.sidebar.text_input("Aiven MySQL Password", type="password")

if not api_key or not db_pass:
    st.error("SYSTEM OFFLINE: Admin Authentication Required.")
    st.stop()

# 4. DIAGNOSTIC ENGINE
st.title("🦉 SLEOWL: PUBLIC HEALTH PORTAL")
st.markdown("---")

col1, col2 = st.columns([3, 2], gap="large")

with col1:
    st.subheader("📋 Public Diagnostic Form")
    with st.form("main_form"):
        name = st.text_input("Full Name")
        c1, c2 = st.columns(2)
        with c1:
            w = st.number_input("Weight (kg)", min_value=1.0)
            ex = st.number_input("Exercise (Hrs/Week)", min_value=0)
        with c2:
            h = st.number_input("Height (cm)", min_value=1.0)
            state = st.selectbox("Physical State", ["Peak", "Normal", "Tired", "Injured"])
        mental = st.slider("Mental Energy", 1, 10, 5)
        notes = st.text_area("Additional Context (Goals/Allergies)")
        submitted = st.form_submit_button("GENERATE SLEOWL HEALTH PLAN")

    if submitted:
        bmi = round(w / ((h/100)**2), 2)
        # THE QUOTA PROTECTION BLOCK
        try:
            client = genai.Client(api_key=api_key)
            prompt = (f"User: {name}. BMI: {bmi}. Exercise: {ex} hrs. State: {state}. Mental: {mental}/10. "
                      f"Suggest a personalized VEGETARIAN diet and 1-week health plan.")
            
            response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
            plan_text = response.text
            
            st.success("Prescription Ready!")
            st.markdown(plan_text)

            # PDF Download
            report_bytes = create_report(name, plan_text, bmi)
            st.download_button(label="📥 DOWNLOAD REPORT (PDF)", data=report_bytes, file_name=f"Sleowl_{name}.pdf", mime="application/pdf")

            # MySQL Sync
            conn = mysql.connector.connect(host='sleowl-ind-sleowl-db.k.aivencloud.com', user='avnadmin', password=db_pass, port='15618', database='defaultdb')
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS public_diagnostics (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100), bmi FLOAT, plan TEXT)")
            cursor.execute("INSERT INTO public_diagnostics (name, bmi, plan) VALUES (%s, %s, %s)", (name, bmi, plan_text))
            conn.commit()
            conn.close()
            st.toast("Telemetry saved to Aiven Cloud")
        except Exception as e:
            if "429" in str(e):
                st.warning("🦉 Sleowl is at peak capacity. Please wait 60 seconds.")
            else:
                st.error(f"Engine Fault: {e}")

with col2:
    st.subheader("🌍 Global Telemetry")
    if st.checkbox("Show Health Trends"):
        try:
            conn = mysql.connector.connect(host='sleowl-ind-sleowl-db.k.aivencloud.com', user='avnadmin', password=db_pass, port='15618', database='defaultdb')
            df = pd.read_sql("SELECT bmi FROM public_diagnostics", conn)
            st.line_chart(df['bmi'])
            st.write(f"Total Diagnostics: {len(df)}")
            conn.close()
        except:
            st.info("Syncing with cloud...")

st.markdown(f'<div class="footer"><p>Built by Devansh Nadpara | Powered by Sleowl AI Engine 🦉</p></div>', unsafe_allow_html=True)
