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
        # Extract text from all visible tags (p, div, ul, li, etc.)
        # We'll collect text from common content tags
        content_tags = soup.find_all(['p', 'div', 'ul', 'li'])
        text = "\n".join(tag.get_text(separator=" ", strip=True) for tag in content_tags)
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

def summarize_message(campaign_text):
    prompt = f"""
You are an expert in summarizing advocacy campaigns.
Your task is to analyze the following campaign text and provide a summary and key points.
Remove any unnecessary details and text that is not relevant to the campaign's main message.
Here is the campaign text:
\"\"\"{campaign_text}\"\"\"
    """
    response = model.generate_content([
        {"role": "user", "parts": [prompt]}
    ])
    return response.text.strip()

# --- Streamlit UI ---
st.title("📝 Advocacy Message Generator")

with st.form("input_form"):
    url = st.text_input("Advocacy Campaign Page URL", placeholder="https://example.org/campaign")
    constituent_name = st.text_input("Your Name", placeholder="Jane Smith")
    constituency = st.text_input("Your City/Constituency", placeholder="Bristol, UK")
    submitted = st.form_submit_button("Generate Advocacy Message")

if submitted:
    with st.spinner("Fetching campaign summary..."):
        summary = summarize_message(get_campaign_summary(url))
        st.subheader("📄 Campaign Summary")
        st.write(summary)

    if "Error" not in summary and summary.strip():
        with st.spinner("Generating your advocacy message..."):
            message = generate_message(summary, constituent_name, constituency)
            st.subheader("📬 Your Advocacy Message")
            st.text_area("Message", message, height=300)
    else:
        st.error("Failed to fetch campaign summary. Please check the URL and try again.")
