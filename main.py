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
    oauth_creds = None
    
    if provider_option != "Ollama":
        if provider_option == "Antigravity":
            # Special handling for Antigravity - offer both options
            auth_method = st.radio(
                "Authentication Method:",
                ("API Key", "Login with Google"),
                help="Choose how to authenticate"
            )
            
            if auth_method == "API Key":
                api_key = st.text_input(f"Enter {provider_option} API Key:", type="password")
                if not api_key:
                    st.warning("Please enter an API Key to proceed.")
                    st.stop()
            else:
                # Multiple auth options for Antigravity
                st.info("🔐 Authentication for Antigravity")
                
                auth_method = st.radio(
                    "Choose authentication method:",
                    ("API Key", "Service Account JSON", "OAuth (Browser Login)"),
                    help="API Key is simplest. Service Account is for automation."
                )
                
                if auth_method == "API Key":
                    st.markdown("Get your key from [Google AI Studio](https://aistudio.google.com/app/apikey)")
                    api_key = st.text_input("Enter Gemini API Key:", type="password")
                    if not api_key:
                        st.warning("Please enter an API Key to proceed.")
                        st.stop()
                        
                elif auth_method == "Service Account JSON":
                    st.markdown("**Using Service Account (No consent screen needed):**")
                    st.markdown("1. Go to [Google Cloud Console](https://console.cloud.google.com/iam-admin/serviceaccounts)")
                    st.markdown("2. Create a Service Account")
                    st.markdown("3. Download the JSON key file")
                    st.markdown("4. Upload it below")
                    
                    uploaded_file = st.file_uploader("Upload Service Account JSON", type=['json'])
                    
                    if uploaded_file:
                        try:
                            import json
                            from google.oauth2 import service_account
                            
                            # Load service account credentials
                            service_account_info = json.load(uploaded_file)
                            credentials = service_account.Credentials.from_service_account_info(
                                service_account_info,
                                scopes=['https://www.googleapis.com/auth/generative-language']
                            )
                            
                            st.session_state.oauth_creds = credentials
                            oauth_creds = credentials
                            st.success("✅ Service Account authenticated!")
                            
                        except Exception as e:
                            st.error(f"❌ Failed to load Service Account: {e}")
                            st.stop()
                    else:
                        st.warning("Please upload your Service Account JSON file.")
                        st.stop()
                    
                else:  # OAuth Browser Login
                    st.markdown("Download OAuth credentials from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)")
                    uploaded_file = st.file_uploader("Upload OAuth Client JSON", type=['json'])
                    
                    if uploaded_file and st.button("🔑 Login with Google"):
                        try:
                            import json
                            from google_auth_oauthlib.flow import InstalledAppFlow
                            
                            oauth_config = json.load(uploaded_file)
                            with open("temp_oauth.json", "w") as f:
                                json.dump(oauth_config, f)
                            
                            flow = InstalledAppFlow.from_client_secrets_file(
                                'temp_oauth.json',
                                scopes=['https://www.googleapis.com/auth/generative-language']
                            )
                            
                            # Use port 0 to automatically find an available port
                            credentials = flow.run_local_server(port=0)
                            
                            st.session_state.oauth_creds = credentials
                            oauth_creds = credentials
                            st.success("✅ OAuth authenticated!")
                            
                            import os
                            os.remove("temp_oauth.json")
                            
                        except Exception as e:
                            st.error(f"❌ OAuth failed: {e}")
                            st.stop()
                    
                    if "oauth_creds" not in st.session_state:
                        st.warning("Please upload OAuth JSON and click 'Login with Google'.")
                        st.stop()
                    else:
                        oauth_creds = st.session_state.oauth_creds
        else:
            # Other providers - API Key only
            api_key = st.text_input(f"Enter {provider_option} API Key:", type="password")
            if not api_key:
                st.warning("Please enter an API Key to proceed.")
                st.stop()
    
    # Initialize Provider
    if st.button("Connect & Fetch Models"):
        with st.spinner(f"Connecting to {provider_option}..."):
            provider = council.get_provider_implementation(provider_option, api_key, oauth_creds)
            if provider:
                st.session_state.provider_instance = provider
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
    
    # Council Mode Selection
    council_mode = st.radio(
        "Council Mode:",
        ("Classic Council", "Debate Council"),
        help="Classic: Multiple members deliberate. Debate: Proponent vs Opponent with short-circuit."
    )
    
    # Fetch available models from the ACTIVE provider
    available_models = st.session_state.provider_instance.list_models()
    
    if not available_models:
        st.error(f"No models found for {provider_option}. Check connection/key.")
        st.stop()
    elif isinstance(available_models[0], str) and available_models[0].startswith("Error"):
        st.error(available_models[0])
        st.stop()

    default_index = 0
    
    if council_mode == "Classic Council":
        st.subheader("Chairman")
        chairman_model = st.selectbox("Select Chairman Model", available_models, index=default_index, key="chairman")

        st.subheader("Council Members")
        num_members = st.slider("Number of Council Members", min_value=2, max_value=3, value=2)
        
        council_members_models = []
        for i in range(num_members):
            member_index = (i + 1) % len(available_models)
            model = st.selectbox(f"Council Member {i+1}", available_models, index=member_index, key=f"member_{i}")
            council_members_models.append(model)
    else:  # Debate Council
        st.subheader("Debate Council Roles")
        
        proponent_index = 0
        opponent_index = min(1, len(available_models) - 1)
        chairman_index = min(2, len(available_models) - 1)
        
        proponent_model = st.selectbox(
            "Proponent (Initial Draft)", 
            available_models, 
            index=proponent_index, 
            key="proponent",
            help="Best general-purpose model (e.g., Claude 3.5 Sonnet, GPT-4o)"
        )
        
        opponent_model = st.selectbox(
            "Opponent (Logic Auditor)", 
            available_models, 
            index=opponent_index, 
            key="opponent",
            help="Different model for adversarial review"
        )
        
        chairman_model = st.selectbox(
            "Chairman (Final Arbiter)", 
            available_models, 
            index=chairman_index, 
            key="debate_chairman",
            help="Only called if Opponent finds flaws"
        )

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # Classic Council - Show deliberation
        if "details" in msg:
             with st.expander("View Council Deliberation"):
                for detail in msg["details"]:
                    st.markdown(f"**{detail['role']} ({detail['model']})**")
                    st.markdown(f"_{detail['content']}_")
                    st.divider()
        
        # Debate Council - Show chain of thought
        if "debate_trace" in msg:
            with st.expander("🔍 View Chain of Thought (Debate Trace)"):
                for step in msg["debate_trace"]:
                    if step['step'] == 'Proponent':
                        st.markdown(f"**📝 Step 1: Proponent ({step['model']})**")
                        st.markdown(f"_{step['output']}_")
                    elif step['step'] == 'Opponent (Logic Auditor)':
                        st.markdown(f"**🔍 Step 2: Opponent - Logic Audit ({step['model']})**")
                        st.markdown(f"_{step['output']}_")
                    elif step['step'] == 'Short-Circuit':
                        st.success(f"⚡ **Step 3: {step['message']}**")
                    elif step['step'] == 'Chairman':
                        st.markdown(f"**👨‍⚖️ Step 4: Chairman ({step['model']})**")
                        st.markdown(f"_{step['output']}_")
                    st.divider()
                
                if msg.get("short_circuit", False):
                    st.info("💡 **Cost Savings**: Short-circuit activated! Only 2 API calls instead of 3 (33% savings).")

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
        
        # We use the active provider instance for all members
        current_provider = st.session_state.provider_instance
        
        if council_mode == "Classic Council":
            council_opinions = []
            
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
        
        else:  # Debate Council
            # 1. Create debate council
            status_text.write(f"📝 Proponent ({proponent_model}) is drafting initial response...")
            proponent = council.Proponent(current_provider, proponent_model)
            
            status_text.write(f"🔍 Opponent ({opponent_model}) will audit the response...")
            opponent = council.Opponent(current_provider, opponent_model)
            
            debate_chairman = council.DebateChairman(current_provider, chairman_model)
            
            debate_council = council.DebateCouncil(proponent, opponent, debate_chairman)
            
            # 2. Execute debate
            result = debate_council.deliberate(prompt, chat_history=chat_history_for_models)
            
            # 3. Display trace
            for step in result['trace']:
                if step['step'] == 'Proponent':
                    status_text.write(f"✅ Proponent ({step['model']}) completed draft")
                elif step['step'] == 'Opponent (Logic Auditor)':
                    status_text.write(f"✅ Opponent ({step['model']}) completed audit")
                elif step['step'] == 'Short-Circuit':
                    status_text.write(f"⚡ {step['message']}")
                elif step['step'] == 'Chairman':
                    status_text.write(f"✅ Chairman ({step['model']}) synthesized final response")
            
            if result['short_circuit']:
                status_text.update(label="✓ Debate Complete (Short-Circuit Activated - Saved 33%!)", state="complete", expanded=False)
            else:
                status_text.update(label="Debate Complete", state="complete", expanded=False)
            
            final_response = result['final_response']
            message_placeholder.markdown(final_response)
            
            # Save with trace for transparency
            st.session_state.messages.append({
                "role": "assistant", 
                "content": final_response,
                "debate_trace": result['trace'],
                "short_circuit": result['short_circuit']
            })
