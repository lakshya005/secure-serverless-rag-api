import streamlit as st
import requests
import json

# --- CONFIGURATION ---
st.set_page_config(page_title="Zero-Trust RAG Demo", layout="wide")
 
st.title("🛡️ Secure Document Intelligence Platform")
st.markdown("### Zero-Trust Retrieval with Row-Level Security")

# --- SIDEBAR: USER IDENTITY SIMULATOR ---
with st.sidebar:
    st.header("👤 User Identity Simulator")
    st.info("In a real app, this comes from the SSO/JWT Token.")
    
    # User selects who they are pretending to be
    user_dept = st.selectbox("Department", ["hr", "finance", "engineering", "legal"])
    user_clearance = st.selectbox("Clearance Level", ["L1", "L2", "L3", "L4", "L5"])
    
    st.markdown("---")
    st.markdown("**System Status:** 🟢 Online")
    
    # API URL Input (So you don't have to hardcode it)
    api_url = st.text_input("Backend API URL", value="https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/dev/chat")

# --- MAIN CHAT INTERFACE ---

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask a question about internal documents..."):
    # 1. Display User Message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Prepare Payload
    payload = {
        "query": prompt,
        "user_dept": user_dept,
        "user_clearance": user_clearance
    }

    # 3. Call Backend API
    with st.chat_message("assistant"):
        with st.spinner(f"Querying Secure Knowledge Base as {user_dept.upper()} ({user_clearance})..."):
            try:
                # Added verify=False to bypass Mac SSL error
                response = requests.post(api_url, json=payload, verify= False)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Parse the body string if it's double-encoded (common with Lambda Proxy)
                    if isinstance(data.get('body'), str):
                        body_data = json.loads(data['body'])
                    else:
                        body_data = data
                        
                    answer = body_data.get("answer", "No answer found.")
                    sources = body_data.get("sources", 0)
                    
                    # Display Answer
                    st.markdown(answer)
                    
                    # Show Security Metadata (Cool for demos!)
                    if sources > 0:
                        st.success(f"🔓 ACCESS GRANTED: Found {sources} secure document(s) matching [{user_dept}/{user_clearance}]")
                    else:
                        st.error(f"🔒 ACCESS DENIED: No documents match your clearance [{user_dept}/{user_clearance}]")
                        
                    # Save to history
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                else:
                    st.error(f"API Error: {response.status_code}")
                    st.text(response.text)
                    
            except Exception as e:
                st.error(f"Connection Error: {e}")