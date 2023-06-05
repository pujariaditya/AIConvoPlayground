import os
from dotenv import load_dotenv

load_dotenv()

def openAIKEY():
    return os.getenv('OPENAI_API_KEY')
