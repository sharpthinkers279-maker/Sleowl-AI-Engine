import streamlit as st
import mysql.connector
import pandas as pd
from fpdf import FPDF
import datetime

# 1. PLATFORM CONFIGURATION
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

# 2. SLEOWL DETERMINISTIC LOGIC ENGINE (Replaces Gemini)
def generate_sleowl_plan(name, bmi, ex, state, mental):
    plan = f"### 🦉 Sleowl Bio-Kinetic Profile: {name}\n\n"
    
    # Diet Logic (Strict Vegetarian)
    plan += "**🥦 Nutritional Prescription (Vegetarian):**\n"
    if bmi < 18.5:
        plan += "- Status: Underweight. Focus on caloric surplus.\n- Intake: High-protein paneer, almonds, peanut butter, and complex carbs (oats/rice) to build mass.\n"
    elif bmi > 25.0:
        plan += "- Status: Elevated BMI. Focus on caloric deficit.\n- Intake: High-fiber salads, lentils (dal), green tea, and strict avoidance of processed sugars.\n"
    else:
        plan += "- Status: Optimal BMI. Focus on maintenance.\n- Intake: Balanced macros with tofu, seasonal vegetables, and whole wheat rotis.\n"
        
    # Recovery & Mental Logic
    plan += "\n**🧠 Recovery & Cognitive Protocol:**\n"
    if mental <= 5 or state in ["Fatigued", "Injured"]:
        plan += f"- Note: Low energy/fatigue detected (Mental Score: {mental}/10).\n- Action: Prioritize 8+ hours of sleep, deep breathing exercises, and suspend heavy weightlifting. Focus on light yoga.\n"
    else:
        plan += f"- Note: High performance state detected (Mental Score: {mental}/10).\n- Action: Maintain {ex} hours of weekly exercise. Focus on progressive overload and aviation-level cognitive focus.\n"
        
    return plan

# 3. PDF ENGINE
def create_report(user_name, plan, bmi):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 15, "Sleowl Clinical Diagnostic Report", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Patient Name: {user_name} | Calculated BMI: {bmi}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, plan.replace('*', '')) # Strip markdown for PDF
    return pdf.output(dest='S').encode('latin-1')

# 4. ADMIN VAULT
with st.sidebar:
    st.header("🔐 Admin Vault")
    db_pass = st.text_input("Aiven MySQL Password", type="password")

if not db_pass:
    st.error("SYSTEM OFFLINE: Database Authentication Required.")
    st.stop()

# 5. DIAGNOSTIC PORTAL
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
            state = st.selectbox("Physical State", ["Peak", "Normal", "Fatigued", "Injured"])
        mental = st.slider("Mental Energy", 1, 10, 5)
        submitted = st.form_submit_button("GENERATE SLEOWL HEALTH PLAN")

    if submitted:
        bmi = round(w / ((h/100)**2), 2)
        
        # Instant Logic Generation (No Quotas, No Limits)
        plan_text = generate_sleowl_plan(name, bmi, ex, state, mental)
        
        st.success("Prescription Ready!")
        st.markdown(plan_text)

        # PDF Download
        report_bytes = create_report(name, plan_text, bmi)
        st.download_button(label="📥 DOWNLOAD REPORT (PDF)", data=report_bytes, file_name=f"Sleowl_{name}.pdf", mime="application/pdf")

        # Database Sync
        try:
            conn = mysql.connector.connect(host='sleowl-ind-sleowl-db.k.aivencloud.com', user='avnadmin', password=db_pass, port='15618', database='defaultdb')
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS public_diagnostics (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100), bmi FLOAT, plan TEXT)")
            cursor.execute("INSERT INTO public_diagnostics (name, bmi, plan) VALUES (%s, %s, %s)", (name, bmi, plan_text))
            conn.commit()
            conn.close()
            st.toast("Telemetry saved to Aiven Cloud")
        except Exception as e:
            st.error(f"Database Fault: {e}")

with col2:
    st.subheader("🌍 Global Telemetry")
    if st.checkbox("Show Health Trends"):
        try:
            conn = mysql.connector.connect(host='sleowl-ind-sleowl-db.k.aivencloud.com', user='avnadmin', password=db_pass, port='15618', database='defaultdb')
            df = pd.read_sql("SELECT bmi FROM public_diagnostics", conn)
            st.line_chart(df['bmi'])
            st.metric("Total Diagnostics Served", len(df))
            conn.close()
        except:
            st.info("Syncing with cloud...")

st.markdown(f'<div class="footer"><p>Built with ❤️ by Devansh Nadpara | Powered by Sleowl Deterministic Engine 🦉</p></div>', unsafe_allow_html=True)
