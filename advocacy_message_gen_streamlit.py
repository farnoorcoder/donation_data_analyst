import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# --- CONFIGURE GOOGLE GENAI ---
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash')

# --- Functions ---
def get_campaign_summary(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        text = "\n".join(p.get_text() for p in paragraphs[:5])
        return text.strip()
    except Exception as e:
        return f"Error fetching content: {e}"

def generate_message(campaign_text, constituent_name, constituency):
    prompt = f"""
You are a constituent named {constituent_name} from {constituency}.
You are writing a passionate, respectful email to your local government office about this advocacy campaign:

\"\"\"{campaign_text}\"\"\"

Write a compelling and personal message asking them to take action.
"""
    response = model.generate_content([{"role": "user", "parts": [prompt]}])
    return response.text

# --- Streamlit UI ---
st.title("📝 Advocacy Message Generator")

with st.form("input_form"):
    url = st.text_input("Advocacy Campaign Page URL", placeholder="https://example.org/campaign")
    constituent_name = st.text_input("Your Name", placeholder="Jane Smith")
    constituency = st.text_input("Your City/Constituency", placeholder="Bristol, UK")
    submitted = st.form_submit_button("Generate Advocacy Message")

if submitted:
    with st.spinner("Fetching campaign summary..."):
        summary = get_campaign_summary(url)
        st.subheader("📄 Campaign Summary")
        st.write(summary)

    if "Error" not in summary and summary.strip():
        with st.spinner("Generating your advocacy message..."):
            message = generate_message(summary, constituent_name, constituency)
            st.subheader("📬 Your Advocacy Message")
            st.text_area("Message", message, height=300)
    else:
        st.error("Failed to fetch campaign summary. Please check the URL and try again.")
