import streamlit as st
import google.generativeai as genai


# Configuration Loader
def load_config():
    """Load required secrets from Streamlit configuration."""
    try:
        return {
            "api_key": st.secrets["AI_API_KEY"],
            "system_instruction": st.secrets["MY_SYSTEM_INSTRUCTIONS"],
            "app_title": st.secrets["APP_TITLE"],
            "greeting": st.secrets["GREETING"],
            "visited_greeting": st.secrets["HAS_VISITED_GREETING"],
            "initial_chat": st.secrets["CHAT_SESSION"],
        }
    except KeyError as e:
        st.error(f"Missing configuration: {e}")
        st.stop()


# Model Initialization
def initialize_model(api_key: str, system_instruction: str):
    """Configure and return the Gemini model."""
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=system_instruction
    )


# Chat Session Management
def initialize_chat_session(model, initial_part):
    """Create a new chat session."""
    return model.start_chat(
        history=[
            {
                "role": "model",
                "parts": [initial_part]
            }
        ]
    )


def display_chat_history(chat_session):
    """Render chat history in the UI."""
    for message in chat_session.history:
        role = "assistant" if message.role == "model" else "user"
        with st.chat_message(role):
            st.markdown(message.parts[0].text)


# Main Application
def main():
    config = load_config()

    # App Title
    st.title(config["app_title"])

    # Initialize Model
    model = initialize_model(
        config["api_key"],
        config["system_instruction"]
    )

    # Initialize Session State
    st.session_state.setdefault("has_visited", False)

    if "chat_session" not in st.session_state:
        st.session_state.chat_session = initialize_chat_session(
            model,
            config["initial_chat"]
        )

    # Display Chat History
    display_chat_history(st.session_state.chat_session)

    # User Input
    user_input = st.chat_input("Ask me anything about my work experience...")

    if user_input:
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)

        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Nidhi is typing..."):
                response = st.session_state.chat_session.send_message(user_input)
                st.markdown(response.text)

    # Start New Chat Button
    if st.button("Start New Chat"):
        greeting = (
            config["visited_greeting"]
            if st.session_state.has_visited
            else config["greeting"]
        )

        st.session_state.has_visited = True
        st.session_state.chat_session = initialize_chat_session(model, greeting)

        st.rerun()


# Entry Point
if __name__ == "__main__":
    main()