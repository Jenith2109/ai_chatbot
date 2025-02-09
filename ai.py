import streamlit as st
from snowflake.snowpark import Session
from snowflake.core import Root

# Snowflake Connection Parameters
CONNECTION_PARAMETERS = {
    "account": "aipedvd-ng71747",
    "user": "jenith21",
    "password": "Jenith@21",
    "warehouse": "WH",
    "database": "DB",
    "schema": "SC"
}

# Initialize Snowflake Session
session = Session.builder.configs(CONNECTION_PARAMETERS).create()

# Cortex AI Service Configuration
CORTEX_SEARCH_DATABASE = "DB"
CORTEX_SEARCH_SCHEMA = "SC"
CORTEX_SEARCH_SERVICE = "CC_SEARCH_SERVICE_CS"

root = Root(session)
svc = root.databases[CORTEX_SEARCH_DATABASE].schemas[CORTEX_SEARCH_SCHEMA].cortex_search_services[CORTEX_SEARCH_SERVICE]

# List of Available AI Models
AI_MODELS = [
    "mixtral-8x7b", "snowflake-arctic", "mistral-large", "llama3-8b", "llama3-70b", "reka-flash",
    "mistral-7b", "llama2-70b-chat", "gemma-7b", "deepseek-67b"
]

# Sidebar Configuration
st.sidebar.header("⚙️ Configuration")
st.sidebar.selectbox("Select AI Model", AI_MODELS, key="sidebar_model_name")

# Initialize session state for chat history and toggle
def init_session():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "upload_section" not in st.session_state:
        st.session_state.upload_section = False
    if "chat_input" not in st.session_state:
        st.session_state.chat_input = ""  # Initialize the input field

init_session()

# Function to Generate AI Prompt
def create_prompt(question: str) -> str:
    return f"""You are a AI assistant. Answer according to the minset of user.
              Engage in a friendly conversation. Maintain a proper limit and stay calm.

    Question: {question}
    
    Answer:
    """

# Function to Get AI Response
def get_ai_response(question: str) -> str:
    prompt = create_prompt(question)
    query = "SELECT snowflake.cortex.complete(?, ?) AS response"
    df_response = session.sql(query, params=[st.session_state.sidebar_model_name, prompt]).collect()
    return df_response[0]["RESPONSE"] if df_response else "No response received."

# Function to Handle File Uploads
def handle_uploaded_file(uploaded_file):
    if uploaded_file is not None:
        file_details = {
            "File Name": uploaded_file.name,
            "File Type": uploaded_file.type,
            "File Size": uploaded_file.size
        }
        st.write(file_details)
        
        if uploaded_file.type == "text/plain":
            content = uploaded_file.getvalue().decode("utf-8")
            st.text_area("File Content", content, height=300)
        else:
            st.warning("Unsupported file format. Please upload a text file.")

# Streamlit Main App
def main():
    st.title("🔗 FusionAI")
    st.write("Switch between AI models and explore AI-driven responses!")

    # Toggle Button for File Upload Section
    if st.button("📂"):
        st.session_state.upload_section = not st.session_state.upload_section  # Toggle state

    # Expandable File Upload Section
    if st.session_state.upload_section:
        with st.expander("Upload a File", expanded=True):
            uploaded_file = st.file_uploader("Upload a file", type=["txt", "pdf", "csv", "xlsx", "json"])
            handle_uploaded_file(uploaded_file)

    # Chat Interface
    question = st.text_input("Ask me anything !", value=st.session_state.chat_input, placeholder="Type your question here...")
    if question:
        response = get_ai_response(question)
        st.session_state.chat_history.insert(0, (question, response))  # Insert at the top to display the newest first
        st.session_state.chat_input = ""  # Clear the input box after submission

    # Display Chat History
    for q, a in st.session_state.chat_history:
        st.markdown(f"""
        <div style="padding: 10px; margin: 5px 0; background-color: #1E1E1E; border-radius: 8px; color: white;">
            <strong>You:</strong> {q}<br>
            <strong>AI:</strong> {a}
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

# Close Snowflake Session
session.close()
