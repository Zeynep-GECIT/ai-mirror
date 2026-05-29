
import streamlit as st
import pandas as pd
from thefuzz import process
import google.generativeai as genai
from dotenv import load_dotenv
import os
load_dotenv()
genai.configure(api_key=os.getenv('API_KEY'))

df = pd.read_csv("occupations.csv", encoding='latin-1')

def get_automation_risk(job_title):
    match = process.extractOne(job_title, df["Occupation"])
    matched_occupation = match[0]
    probability = df[df["Occupation"] == matched_occupation]["Probability"].values[0]
    return matched_occupation, probability

def get_color(risk_percent):
    r = int(255 * risk_percent / 100)
    g = int(255 * (1 - risk_percent / 100))
    return f"rgb({r},{g},50)"

def get_ai_analysis(occupation, risk_percent):
    import time
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"""
    The occupation '{occupation}' has a {risk_percent}% probabilityof automation.

    Please provide a brief analysis with exactly 3 sections:
    1. Why this occupation is at this risk level
    2. Skills to develop to stay relevant
    3. How this occupation will look in 5 years

    Keep each section to 2-3 sentences. Be direct and practical.
    """
    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if '429' in str(e) and attempt < 2:
                with st.spinner('Rate limit reached, retrying in 31 seconds...'):
                    time.sleep(31)
            else:
                return 'Analysis temporarily unavailable. Please try again later.'

st.set_page_config(page_title="AI MIRROR", layout="centered")

st.markdown("""
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');
    
    html, body, [class*="css"] {
        background: linear-gradient(135deg, #0B0C10, #1F2833, #45A29E);
    }
    .stApp {
        background: linear-gradient(135deg, #0B0C10, #1F2833, #45A29E);
        color: #66FCF1;
    }
    h1 {
        font-family: 'Orbitron', sans-serif !important;
        border-bottom: 2px solid #45A29E;
        font-weight: 700;
        color: #66FCF1;
        font-size: 3.5rem;
        padding-bottom: 15px;
        margin-bottom: 25px;
        text-shadow: 0 0 10px rgba(102, 252, 241, 0.3);
    }
     h3 {
        font-family: 'Orbitron', sans-serif !important;
        color: #66FCF1 !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
    }

    .stTextInput input {
        color: #000000 !important;
    }
    .risk-box {
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        font-family: 'Orbitron', sans-serif;
        font-size: 1.2rem;
        font-weight: bold;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("AI MIRROR")
st.subheader("Hold Up the Mirror of AI to Your Career")
st.caption('❗ This tool provides estimates based on academic research. Results are not guaranteed predictions of your careerfuture.')
st.markdown("---")

st.markdown('<p style="color: #66FCF1; font-family: Orbitron, sans-serif; font-size: 0.9rem;">Enter your profession (e.g. accountant, graphic designer, nurse)</p>', unsafe_allow_html=True)

with st.form('job_form'):
    job = st.text_input('', placeholder = 'e.g. accountant, graphic designer, nurse')
    submitted = st.form_submit_button('Analyze')

if submitted and job:
    occupation, risk = get_automation_risk(job)
    risk_percent = round(risk * 100, 1)
    color = get_color(risk_percent)
    
    st.markdown(f"### Closest match: {occupation}")
    st.markdown(f"""
        <div class="risk-box" style="background-color: {color}; color: white;">
            Automation Risk: {risk_percent}%
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.progress(int(risk_percent))

    cache_key = f"{occupation}_{risk_percent}"
    if cache_key not in st.session_state:
        with st.spinner('Analyzing your career...'):
            st.session_state[cache_key] = get_ai_analysis(occupation, risk_percent)
    
    with st.spinner('Analyzing your career...'):
        analysis = get_ai_analysis(occupation, risk_percent)
        
        st.markdown('---')
        st.markdown('### 🔍 AI Analysis')
        st.markdown(analysis)
