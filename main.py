import streamlit as st
import council
from typing import List

# Set page configuration
st.set_page_config(page_title="LLM Council", page_icon="🏛️", layout="wide")

# Custom CSS for aesthetics
st.markdown("""
<style>
    .stChatMessage {
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .council-opinion {
        font-size: 0.9em;
        color: #555;
        border-left: 3px solid #ddd;
        padding-left: 10px;
        margin-top: 5px;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏛️ LLM Council POC")
st.markdown("Two or three models deliberate, and the Chairman decides.")

# --- Session State for Provider ---
if "provider_instance" not in st.session_state:
    st.session_state.provider_instance = None

# Sidebar - Configuration
with st.sidebar:
    st.header("1. Tool Selection")
    
    provider_option = st.radio(
        "Select AI Provider:",
        ("Ollama", "Claude Code", "OpenCode", "Antigravity", "OpenRouter"),
        help="Ollama is offline. Others require API Keys."
    )
    
    api_key = None
    if provider_option != "Ollama":
        api_key = st.text_input(f"Enter {provider_option} API Key:", type="password")
        if not api_key:
            st.warning("Please enter an API Key to proceed.")
            st.stop()
    
    # Initialize Provider
    if st.button("Connect & Fetch Models"):
        with st.spinner(f"Connecting to {provider_option}..."):
            provider = council.get_provider_implementation(provider_option, api_key)
            if provider:
                st.session_state.provider_instance = provider
                # Fetch models immediately to cache them? or just rely on dynamic list below
                st.success("Connected!")
            else:
                st.error("Failed to connect. Check implementation.")

    st.divider()
    
    # Only show Council Config if connected (or if Ollama is default)
    # For Ollama, we can auto-connect if no explicit connect button press
    if st.session_state.provider_instance is None:
        if provider_option == "Ollama":
            st.session_state.provider_instance = council.get_provider_implementation("Ollama")
        else:
            st.info("Connect to a provider to configure the Council.")
            st.stop()

    st.header("2. Council Configuration")
    
    # Fetch available models from the ACTIVE provider
    available_models = st.session_state.provider_instance.list_models()
    
    if not available_models:
        st.error(f"No models found for {provider_option}. Check connection/key.")
        st.stop()
    elif isinstance(available_models[0], str) and available_models[0].startswith("Error"):
        st.error(available_models[0])
        st.stop()

    default_index = 0
    
    st.subheader("Chairman")
    chairman_model = st.selectbox("Select Chairman Model", available_models, index=default_index, key="chairman")

    st.subheader("Council Members")
    num_members = st.slider("Number of Council Members", min_value=2, max_value=3, value=2)
    
    council_members_models = []
    for i in range(num_members):
        member_index = (i + 1) % len(available_models)
        model = st.selectbox(f"Council Member {i+1}", available_models, index=member_index, key=f"member_{i}")
        council_members_models.append(model)

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "details" in msg:
             with st.expander("View Council Deliberation"):
                for detail in msg["details"]:
                    st.markdown(f"**{detail['role']} ({detail['model']})**")
                    st.markdown(f"_{detail['content']}_")
                    st.divider()

# Input Area
if prompt := st.chat_input("Ask the Council..."):
    # Add user message to history and display
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare chat history for models
    chat_history_for_models = [
        {"role": m["role"], "content": m["content"]} 
        for m in st.session_state.messages 
        if m["role"] != "system" 
    ]
    chat_history_for_models = chat_history_for_models[:-1]

    # Process with Council
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        status_text = st.status(f"The Council ({provider_option}) is deliberating...", expanded=True)
        
        council_opinions = []
        
        # We use the active provider instance for all members
        current_provider = st.session_state.provider_instance

        # 1. Council Members generate opinions
        for i, model_name in enumerate(council_members_models):
            role_name = f"Council Member {i+1}"
            status_text.write(f"🤔 {role_name} ({model_name}) is thinking...")
            
            # Pass the provider instance to the Member class
            member = council.CouncilMember(current_provider, model_name, role=role_name)
            opinion = member.get_opinion(prompt, chat_history=chat_history_for_models)
            
            council_opinions.append({
                "role": role_name,
                "model": model_name,
                "content": opinion
            })
            status_text.write(f"✅ {role_name} has spoken.")

        # 2. Chairman synthesis
        status_text.write(f"👨‍⚖️ The Chairman ({chairman_model}) is synthesizing the final response...")
        # Pass the provider instance to the Chairman class
        chairman = council.Chairman(current_provider, chairman_model)
        final_response = chairman.synthesize(prompt, council_opinions, chat_history=chat_history_for_models)
        
        status_text.update(label="Deliberation Complete", state="complete", expanded=False)
        
        message_placeholder.markdown(final_response)
        
        # Save validation/response
        st.session_state.messages.append({
            "role": "assistant", 
            "content": final_response,
            "details": council_opinions
        })
