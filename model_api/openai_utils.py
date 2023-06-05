import openai
from model_api import chatgptConfig

def is_valid_openai_key(api_key):
    openai.api_key = api_key
    # openai.api_key = chatgptConfig.openAIKEY()

    try:
        openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "initialize"}
            ]
        )
        return True
    except openai.error.AuthenticationError:
        return False
