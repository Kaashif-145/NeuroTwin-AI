import streamlit as st
import streamlit as st
import os
import re
from backend.agents.agent_prompts import get_agent_system_prompt
from backend.utils.vector_memory import get_user_context, save_user_memory
from backend.utils.llm_client import get_chat_response
from frontend.utils.i18n import _t

def _extract_keywords(prompt):
    words = re.findall(r"[A-Za-z]{4,}", prompt.lower())
    stop_words = {"what", "when", "where", "explain", "please", "tell", "this", "that"}
    return [word for word in words if word not in stop_words][:5]

def _find_relevant_context(prompt):
    """Simple keyword-based search for when AI is down."""
    raw_text = st.session_state.get("raw_text", "")
    if not raw_text:
        return None
    
    keywords = _extract_keywords(prompt)
    sentences = re.split(r"(?<=[.!?])\s+|\n+", raw_text)
    hits = []
    for s in sentences:
        if any(k in s.lower() for k in keywords) and len(s) > 20:
            hits.append(s.strip())
    
    return "\n- ".join(hits[:3]) if hits else None

def show_chat_assistant():
    st.title("💬 " + _t("nav_chat"))
    
    # 1. Sidebar Settings
    with st.sidebar:
        st.title("🤖 Agent Settings")
        agent_choice = st.selectbox("Choose AI Assistant", ["Tutor", "Career", "Researcher"])
        system_prompt = get_agent_system_prompt(agent_choice.lower())
        
        st.markdown("---")
        st.info("💡 **Tip:** If AI is slow or out of quota, start **Ollama** locally for free, unlimited chat.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask a study question..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        user_email = st.session_state.get("user_email", "guest")
        memory_context = get_user_context(user_email)
        full_system_prompt = f"{system_prompt}\n\nPast User Context:\n{memory_context}"
        
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            response_placeholder.markdown("🧠 Thinking...")
            
            try:
                llm_history = []
                for m in st.session_state.messages[:-1]:
                    role = "user" if m["role"] == "user" else "model"
                    llm_history.append({"role": role, "parts": [m["content"]]})

                response_text, provider = get_chat_response(
                    prompt=prompt,
                    history=llm_history,
                    system_prefix=full_system_prompt
                )
                response_placeholder.markdown(response_text)
                save_user_memory(user_email, f"User: {prompt[:50]}. AI: {response_text[:100]}...")
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            
            except Exception as e:
                # 🚨 THE FIX: Fallback to document context if AI fails
                context_hit = _find_relevant_context(prompt)
                if context_hit:
                    fallback_msg = f"⚠️ **AI Quota Reached.** I found this in your uploaded documents:\n\n- {context_hit}"
                else:
                    fallback_msg = "❌ **All AI services are offline.** Please check your internet, API keys, or start Ollama locally."
                
                response_placeholder.markdown(fallback_msg)
                st.session_state.messages.append({"role": "assistant", "content": fallback_msg})

show_chat_assistant()
