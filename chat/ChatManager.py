import logging
logger = logging.getLogger(__name__)
class ChatManager:
    def __init__(self, agents, chat_log):
        self.agents = agents
        self.chat_log = chat_log

    def display_chat(self, chat_container):
        chat_container.write("\n\n".join([f"> :speech_balloon: **{log[0]}** {log[1]}" for log in self.chat_log]))

    def chat(self, user_message=None, next_agent=None, chat_container=None,username=None):
        if user_message and next_agent:
            self.chat_log.append((username, user_message))
            self.display_chat(chat_container)
            try:
                response = next_agent.generate_message(self.chat_log,user_message)
                self.chat_log.append((next_agent.char_name, response))
                self.display_chat(chat_container)
            except Exception as e:
                chat_container.error(f"An error occurred while generating a response: {e}")
        elif user_message == "" and next_agent:
            try:
                last_message = ""
                if len(self.chat_log) != 0:
                    last_message = self.chat_log[-1][-1]
                response = next_agent.generate_message(self.chat_log,last_message)
                self.chat_log.append((next_agent.char_name, response))
                self.display_chat(chat_container)
            except Exception as e:
                chat_container.error(f"An error occurred while generating a response: {e}")
        return
