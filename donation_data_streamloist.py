#
#
#      Streamlit App: Chat with your CSV Data
#
#      This application provides a web-based UI to chat with the Gemini model
#      about the contents of an uploaded CSV file, acting as a data analyst.
#
#      ----------------------------------------------------------------------
#
#      --- HOW TO RUN ---
#
#      1. Make sure you have the required libraries installed:
#         pip install streamlit pandas google-generativeai
#
#      2. Save this code as a Python file (e.g., app.py).
#
#      3. Run the application from your terminal:
#         streamlit run app.py
#
#      4. Open your web browser to the local URL provided by Streamlit.
#         - Enter your Google API Key in the sidebar.
#         - Upload your CSV file.
#         - Start asking questions in the chat dialog box at the bottom!
#
#

import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- Page Configuration ---
st.set_page_config(
    page_title="Donation Data Analyst Chat",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Donation Data Analyst Chatbot")
st.caption("Upload your donation data and ask me anything about it.")

# --- Helper Function to Initialize Chat ---
def initialize_chat(api_key, system_prompt):
    """
    Configures the Gemini model and starts a chat session.
    """
    try:
        genai.configure(api_key=api_key)
        # Using a model optimized for multi-turn chat
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Start a chat with an initial history
        chat = model.start_chat(history=[
            {"role": "user", "parts": [system_prompt]},
            {"role": "model", "parts": ["OK, I have the data. What would you like to know?"]}
        ])
        return chat
    except Exception as e:
        st.error(f"Failed to initialize the model. Please check your API key. Error: {e}")
        return None

# --- Sidebar for API Key and File Upload ---
with st.sidebar:
    st.header("Setup")
    google_api_key = st.text_input("Enter your Google API Key", type="password")
    uploaded_file = st.file_uploader("Upload your transaction CSV file", type=["csv"])

    st.markdown("---")
    st.markdown(
        "**Instructions:**\n"
        "1. Get your Google API Key from [Google AI Studio](https://aistudio.google.com/app/apikey).\n"
        "2. Enter the key above.\n"
        "3. Upload your CSV data.\n"
        "4. The chat will begin automatically!"
    )

# --- Main Application Logic ---

# Initialize session state variables if they don't exist
if 'chat' not in st.session_state:
    st.session_state.chat = None
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Logic to start a new chat session
if google_api_key and uploaded_file and st.session_state.chat is None:
    with st.spinner("Analyzing your data and preparing the chatbot..."):
        try:
            # Load the uploaded CSV into a pandas DataFrame
            df = pd.read_csv(uploaded_file)
            df_string = df.to_csv(index=False)

            # Construct the system prompt from your script
            system_prompt = f"""
            "You are an expert data analyst specializing in donation transactions. "
            "Your task is to analyze the provided dataset and answer questions about it. "
            "The dataset contains various donation transactions, including payment types, "
            "amounts, single or recurring, and other relevant details. "
            "Please provide detailed and accurate responses based on this data set and only this data set. "

            Here is the dataset:
            --- DATASET START ---
            {df_string}
            --- DATASET END ---

            Acknowledge that you have received and understood the data. Then, wait for the user's question.
            """
            
            # Initialize the chat object
            st.session_state.chat = initialize_chat(google_api_key, system_prompt)

            # Add the initial model confirmation to the message history
            if st.session_state.chat:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "OK, I have analyzed your data. What would you like to know?"
                })

        except Exception as e:
            st.error(f"An error occurred while setting up the chat: {e}")

# Display existing messages in the chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input dialog box - only appears if the chat is initialized
if st.session_state.chat:
    if user_question := st.chat_input("Ask a question about your data..."):
        # Add user's question to messages and display it
        st.session_state.messages.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)

        # Get and display the model's response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.chat.send_message(user_question)
                    response_text = response.text
                    st.markdown(response_text)
                    # Add model's response to the message history
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                except Exception as e:
                    st.error(f"An error occurred while generating the response: {e}")

# Initial message if the app is not configured
elif not (google_api_key and uploaded_file):
    st.info("Please enter your Google API Key and upload a CSV file to start chatting.")
