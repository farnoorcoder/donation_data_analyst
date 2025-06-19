import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- Page Configuration ---
st.set_page_config(
    page_title="Supporter Data Analyst Chat",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Supporter Data Analyst Chatbot")
st.caption("Upload your supporter data and allow me to analyze it for you.")

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
    google_api_key = st.secrets["GOOGLE_API_KEY"]
    uploaded_file = st.file_uploader("Upload your supporter's CSV file", type=["csv"])

    st.markdown("---")
    st.markdown(
        "**Instructions:**\n"
        "1. Upload your CSV data.\n"
        "2. The chat will begin automatically!"
    )

# --- Main Application Logic ---

# Initialize session state variables if they don't exist
if 'chat' not in st.session_state:
    st.session_state.chat = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'last_uploaded_filename' not in st.session_state:
    st.session_state.last_uploaded_filename = None

# Logic to start or reset a chat session when a new file is uploaded
if google_api_key and uploaded_file:
    # Detect if a new file is uploaded (by filename)
    if uploaded_file.name != st.session_state.get('last_uploaded_filename'):
        with st.spinner("Analyzing your data and preparing the chatbot..."):
            try:
                # Load the uploaded CSV into a pandas DataFrame
                df = pd.read_csv(uploaded_file)
                df_string = df.to_csv(index=False)

                # Construct the system prompt from your script
                system_prompt = f"""
                You are a data analyst AI that summarizes supporter engagement based on historical activity. You will be given a CSV file containing a supporter's record of interactions with an organization, including events attended, actions taken, and donation history.

                Your goal is to analyze this data and produce a concise engagement summary. Your response should assess how active and committed the supporter is, referencing meaningful patterns or milestones. Be objective and data-driven, but human-readable and clear.

                The CSV may contain fields such as:
                - `Campaign Date`, `Campaign ID`, `Campaign Type`
                - `Action Date`, `Action Type` (e.g., petition signed, email opened)
                - `Donation Date`, `Donation Amount`, `Campaign Name`, `Donation Type` (e.g., one-time or recurring)

                In your summary, consider:
                - Recency and frequency of activity
                - Diversity of engagement types (events, actions, donations)
                - Total and recent donation volume
                - Participation in key events or campaigns
                - Any signs of deepening or declining engagement over time

                Output a paragraph summary that classifies the supporter as **Highly Engaged**, **Moderately Engaged**, or **Minimally Engaged**, and explain why.

                Do not simply restate the CSV contents. Instead, interpret the patterns and trends in the data to give a narrative overview of their engagement.


                Here is the dataset:
                --- DATASET START ---
                {df_string}
                --- DATASET END ---    

                Acknowledge that you have received and understood the data. Then, wait for the user's question.
                """

                # Initialize the chat object
                st.session_state.chat = initialize_chat(google_api_key, system_prompt)
                st.session_state.messages = []  # Reset chat history
                st.session_state.last_uploaded_filename = uploaded_file.name

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
    st.info("Please upload a CSV file of your supporter's historical data and start chatting.")
