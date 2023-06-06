import json
import logging
import os
import random
import re
import tempfile
from model_api.model_urls import model_urls, gptmodels
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from chat.ChatAgent import ChatAgent
from chat.ChatInit import ChatInit
from model_api import openai_utils

logger = logging.getLogger(__name__)

# Initializing Directory names
role_files_directory = "role_files"
new_role_files_directory = "new_role_files"

# Initializing App
application_name = "AI Convo Playground"
########################################################################################################################

# Customize Streamlit
st.set_page_config(page_title=application_name, page_icon="🖖", layout="wide")

st.markdown("# 🖖" + application_name, unsafe_allow_html=True)
tabs = st.tabs(["Character Settings", "Chat Window"])

hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

padding = 0
st.markdown(f""" <style>
    .reportview-container .main .block-container{{
        padding-top: {padding}rem;
        padding-right: {padding}rem;
        padding-left: {padding}rem;
        padding-bottom: {padding}rem;
    }} </style> """, unsafe_allow_html=True)

########################################################################################################################
# Streamlit Initialize session state

if 'added_roles' not in st.session_state:
    st.session_state.added_roles = {}

if 'is_chatting' not in st.session_state:
    st.session_state.is_chatting = False

if 'chat_log' not in st.session_state:
    st.session_state.chat_log = []

if 'prev_chat_log' not in st.session_state:
    st.session_state.prev_chat_log = []


########################################################################################################################
# # Initializing Chat Modules
@st.cache_data
def initialize():
    chatinit = ChatInit()
    models_available = chatinit.get_available_models()
    local_characters = chatinit.read_local_characters(role_files_directory)
    chat_manager = chatinit.initialize_chat_manager(role_files_directory)
    return models_available, local_characters, chat_manager


models_available, local_characters, chat_manager = initialize()


########################################################################################################################
# Helper Functions

def clean_string(input_string):
    cleaned_string = re.sub(r'[^a-zA-Z\s]', '', input_string)
    cleaned_string = re.sub(r'\s+', ' ', cleaned_string)
    cleaned_string = cleaned_string.strip()
    return cleaned_string


def char_file_create(char_name, char_persona, char_greeting, world_scenario, example_dialogue):
    file_path = os.path.join(new_role_files_directory, f"{char_name}.json")
    character_data = json.dumps({
        "char_name": char_name,
        "char_persona": char_persona,
        "char_greeting": char_greeting,
        "world_scenario": world_scenario,
        "example_dialogue": example_dialogue
    })
    with open(file_path, "w") as f:
        f.write(character_data)
    st.session_state.added_roles[char_name] = character_data
    success_message = f'"{char_name}" character added successfully.'
    st.success(success_message, icon="✅")
    return


########################################################################################################################
# Validating Helper Functions

def validate_api_key():
    api_key = st.session_state.api_key

    if api_key and (openai_utils.is_valid_openai_key(api_key)):
        st.success("API key validated successfully!", icon="✅")
    else:
        st.warning("API key invalid!", icon="⚠️")


def validate_new_role():
    if st.session_state.new_role:
        new_role = st.session_state.new_role
        if not re.match("^[a-zA-Z]+$", new_role):
            st.warning("The new role should contain only letters.", icon="⚠️")

def check_if_using_chatgpt_api():
    number_gpt_model = len(list((set(list(selected_models.values()))) - (set(list(model_urls.keys())))))
    if number_gpt_model>0:
        return True
    else:
        return False

def session_on_click():
    if check_if_using_chatgpt_api():
        api_key = st.session_state.api_key

    if st.session_state.is_chatting:
        st.session_state.is_chatting = False
        st.session_state.prev_chat_log = list(st.session_state.chat_log)
        st.session_state.chat_log.clear()  # Clear chat log when stopping chat
        return

    if len(selected_roles) < 1:
        st.warning("At least one agent is required to start the session.", icon="⚠️")
    elif check_if_using_chatgpt_api() and not openai_utils.is_valid_openai_key(st.session_state.api_key):
        st.error("Invalid API key.")
    elif not username:
        st.warning("Please enter your name.")
    else:
        st.session_state.is_chatting = True


########################################################################################################################
# Streamlit Tab 1 Character Settings

character_settings = tabs[0]

with character_settings:
    # Get the OpenAI API key

    username = st.text_input(
        label="Your Name",
        help="How the character should call you",
        key='username',
        disabled=st.session_state.is_chatting
    )

    num_characters = st.number_input("Number of Characters", max_value=5, min_value=0, value=0, step=1,
                                     disabled=st.session_state.is_chatting)

    charfiles = []
    with st.form("character_form", ):
        for i in range(num_characters):
            with st.expander(f"Character {i + 1}", expanded=False):
                char_name = st.text_input(
                    label="Character Name",
                    help="The character's name",
                    key=f"char-name-{i}"
                )

                char_persona = st.text_area(
                    label="Character Persona",
                    help="Describe the character's persona here. Think of this as CharacterAI's description + definitions in one box.",
                    height=150,
                    key=f"char-persona-{i}"
                )
                char_greeting = st.text_area(
                    label="Character Greeting",
                    help="Write the character's greeting here. They will say this verbatim as their first response.",
                    height=100,
                    key=f"char-greeting-{i}"
                )

                world_scenario = st.text_area(
                    label="Scenario",
                    help="Optionally, describe the starting scenario in a few short sentences.",
                    height=100,
                    key=f"world-scenario-{i}"
                )
                example_dialogue = st.text_area(
                    label="Example Chat",
                    help="Optionally, write in an example chat here. This is useful for showing how the character should behave, for example.",
                    height=150,
                    key=f"example-dialogue-{i}"
                )

                charfiles.append((char_name, char_persona, char_greeting, world_scenario, example_dialogue))
        submit_button = st.form_submit_button(label="Add characters", disabled=st.session_state.is_chatting)

    if submit_button:
        for i, character in enumerate(charfiles):
            char_name, char_persona, char_greeting, world_scenario, example_dialogue = character
            char_file_create(char_name, char_persona, char_greeting, world_scenario, example_dialogue)

    # Select roles and models for agents
    selected_roles = st.multiselect("Select the roles for the agents:",
                                    list(local_characters.keys()) + list(
                                        st.session_state.added_roles.keys()),
                                    disabled=st.session_state.is_chatting)

    # A dict to hold selected models for each role
    selected_models = {}
    for role in selected_roles:
        selected_model = st.selectbox(f"Select the model for {role}:", models_available, key=f"model_{role}",
                                      disabled=st.session_state.is_chatting)
        selected_models[role] = selected_model

    if check_if_using_chatgpt_api():
        api_key = st.text_input("Enter your OpenAI API key:", on_change=validate_api_key, key="api_key",
                            disabled=st.session_state.is_chatting)
########################################################################################################################
# Streamlit Tab 2 Chat Window

@st.cache_data
def load_character_from_file(role):
    with open(f"{new_role_files_directory}/{role}.json", "r") as file:
        return json.load(file)


def initialize_chat_system():
    added_roles = st.session_state.added_roles
    selected_agents = []

    for role in selected_roles:
        if role in local_characters:
            character = json.loads(local_characters[role])
        elif role in added_roles:
            character = load_character_from_file(role)
        else:
            continue

        char_name = character['char_name']
        char_persona = character['char_persona']
        char_greeting = character['char_greeting']
        world_scenario = character['world_scenario']
        example_dialogue = character['example_dialogue']

        selected_agents.append(
            ChatAgent(char_name, char_persona, char_greeting, world_scenario, example_dialogue, selected_models[char_name])
        )

    return selected_agents


def chat_with_user(user_chat, response_agent):
    chat_manager.agents = initialize_chat_system()
    chat_manager.chat_log = st.session_state.chat_log
    next_agent = next((agent for agent in chat_manager.agents if agent.char_name == response_agent), None)
    logger.error("---------------")
    for agent in chat_manager.agents:
        logger.error(agent.model_name)
    logger.error("---------------")
    chat_manager.chat(user_message=user_chat, next_agent=next_agent, chat_container=chat_container, username=username)


chat_window_settings = tabs[1]

with chat_window_settings:
    status, switch = st.columns([6, 1])
    with status:
        if not st.session_state.is_chatting:
            st.markdown(
                '<span style="background-color: #ffffff; color: #000000; padding: 5px 10px; border-radius: 4px; border: 1px solid #FF0000;"><span style="background-color: #FF0000; border-radius: 50%; width: 10px; height: 10px; display: inline-block; margin-right: 5px;"></span>Offline</span>',
                unsafe_allow_html=True)
        else:
            st.markdown(
                '<span style="background-color: #ffffff; color: #000000; padding: 5px 10px; border-radius: 4px; border: 1px solid #79C753;"><span style="background-color: #79C753; border-radius: 50%; width: 10px; height: 10px; display: inline-block; margin-right: 5px;"></span>Online</span>',
                unsafe_allow_html=True)

    # Add elements to the second column
    with switch:
        st.button('Start/Stop Session', on_click=session_on_click)

    col1, col2 = st.columns([1, 1])

    with col1:
        chat_container = st.empty()

    with col2:
        last_response_agent = None
        if len(selected_roles) > 1:
            raise_hand = st.checkbox("Raise Hand")

            if raise_hand:
                # User raises hand to chat with a specific agent
                chat_manager.chat_log = st.session_state.chat_log
                chat_manager.display_chat(chat_container)
                form = st.form(key='my_form', clear_on_submit=True)
                user_chat = form.text_area("Enter chat...", height=240)
                response_agent = form.selectbox("Reply to:", list(selected_roles))
                sendbtn = form.form_submit_button('Send')

                if sendbtn:
                    if not st.session_state.is_chatting:
                        st.warning("Chat session is not started. Please start the session before sending a message.",
                                   icon="⚠️")
                    else:
                        chat_with_user(user_chat, response_agent)
                        last_response_agent = response_agent

            else:
                # Agents chat among themselves
                chat_manager.chat_log = st.session_state.chat_log
                chat_manager.display_chat(chat_container)

                if not st.session_state.is_chatting:
                    st.warning("Chat session is not started. Please start the session before sending a message.",
                               icon="⚠️")
                else:
                    while not raise_hand:
                        user_chat = ""
                        available_agents = [agent for agent in selected_roles if agent != last_response_agent]
                        response_agent = random.choice(available_agents)
                        chat_with_user(user_chat, response_agent)
                        last_response_agent = response_agent

        else:
            # User chats with the agent
            form = st.form(key='my_form', clear_on_submit=True)
            user_chat = form.text_area("Enter chat...", height=240)
            response_agent = form.selectbox("Reply to:", list(selected_roles))
            sendbtn = form.form_submit_button('Send')

            if sendbtn:
                if not st.session_state.is_chatting:
                    st.warning("Chat session is not started. Please start the session before sending a message.",
                               icon="⚠️")
                else:
                    chat_with_user(user_chat, response_agent)
                    last_response_agent = response_agent

        if st.checkbox('Show Chat Log', disabled=st.session_state.is_chatting):
            if st.session_state.prev_chat_log:
                st.markdown("## Chat Log")
                for role, message in st.session_state.prev_chat_log:
                    st.write(f"> :speech_balloon: **{role}** {message}")
                if st.button('Export Chat Log'):
                    filename = 'chat_log.pdf'
                    save_directory = './tempfiles/'

                    formatted_chat_log = ""
                    for role, message in st.session_state.prev_chat_log:
                        formatted_chat_log += f" {role} : {message}\n\n"

                    try:
                        # Create a temporary file to save the PDF
                        temp_pdf_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False, dir=save_directory)
                        temp_pdf_file.close()

                        # Create a new PDF document
                        pdf = canvas.Canvas(temp_pdf_file.name, pagesize=letter)

                        # Set font and size
                        pdf.setFont("Helvetica", 12)

                        # Set initial y position
                        y = 750

                        # Write the chat log content to the PDF
                        lines = formatted_chat_log.split("\n")
                        for line in lines:
                            pdf.drawString(50, y, line)
                            y -= 15

                        # Save the PDF document to the temporary file
                        pdf.save()

                        # Provide download link
                        st.download_button(
                            label='Download Chat Log (PDF)',
                            data=open(temp_pdf_file.name, 'rb'),
                            file_name=filename,
                            mime='application/pdf'
                        )

                        st.success("Click the link to download the chat log as a PDF file.", icon="✅")
                    except Exception as e:
                        st.error(f"An error occurred while exporting the chat log: {e}")
