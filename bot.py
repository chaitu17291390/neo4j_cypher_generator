import streamlit as st
from final_agent import run_agent

# Page Config (This should be the first Streamlit command)
st.set_page_config("Ebert", page_icon=":movie_camera:")

# Hide GitHub icon
hide_github_icon = """
#GithubIcon {
  visibility: hidden;
}
"""
st.markdown(hide_github_icon, unsafe_allow_html=True)

def write_message(role, content, save=True):
    """
    This is a helper function that saves a message to the
    session state and then writes a message to the UI
    """
    # Append to session state
    if save:
        st.session_state.messages.append({"role": role, "content": content})

    # Write to UI
    with st.chat_message(role):
        st.markdown(content)

# Set up Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi, I'm the SCM Chatbot! How can I help you?"},
    ]

# Submit handler
def handle_submit(message):
    # Handle the response
    with st.spinner('Thinking...'):
        response = run_agent(message)
        write_message('assistant', response)

# Display messages in Session State
for message in st.session_state.messages:
    # Ensure that each message is displayed in its own context
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# Handle any user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    write_message('user', prompt)

    # Generate a response
    handle_submit(prompt)
