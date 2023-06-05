import json
import logging
import os

from chat.ChatAgent import ChatAgent
from chat.ChatManager import ChatManager
from model_api.model_urls import model_urls, gptmodels

logger = logging.getLogger(__name__)


class ChatInit:
    def __init__(self):
        self.models_available = list(model_urls.keys()) + gptmodels

    def get_available_models(self):
        return self.models_available

    @staticmethod
    def read_local_characters(directory):
        # Initialize the role_system_messages dictionary
        local_characters = {}

        # Iterate over the files in the specified directory
        for filename in os.listdir(directory):
            if filename.endswith(".json"):
                # Read the system message from the file
                with open(os.path.join(directory, filename), "r") as file:
                    system_message = file.read()

                character_name = json.loads(system_message)['char_name']
                local_characters[character_name] = system_message

        return local_characters

    def initialize_chat_manager(self, role_files_directory):
        # Read the role system messages
        local_characters = self.read_local_characters(role_files_directory)

        # Initialize chat manager and chat agent
        agents = []
        for key, value in local_characters.items():
            character = json.loads(value)
            char_name = character['char_name']
            char_persona = character['char_persona']
            char_greeting = character['char_greeting']
            world_scenario = character['world_scenario']
            example_dialogue = character['example_dialogue']
            agents.append(ChatAgent(char_name, char_persona, char_greeting, world_scenario, example_dialogue,
                                    self.models_available[0]))

        chat_manager = ChatManager(agents, [])

        return chat_manager
