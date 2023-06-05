# AI Convo Playgroung

Welcome to the AI Convo Playground project! This project focuses on creating an interactive dialogue system where multiple agents engage in conversations with each other. Each agent has a unique character, and these characters access a large language model API to generate appropriate dialogues in the conversation.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Overview

In this project, we aim to simulate conversations between multiple agents using a large language model API. Each agent has a specific character or personality, and they generate dialogues based on their individual traits. The agents interact with each other, taking turns to contribute to the conversation.

## Features

- Multiple agents with unique characters: Each agent has a distinct personality or character, which influences the way they contribute to the conversation.
- Interaction with a large language model: The agents utilize a powerful language model API to generate responses and maintain engaging conversations.
- Turn-based dialogue system: The agents take turns in the conversation, ensuring a smooth and coherent exchange of dialogue.
- Flexible dialogue generation: The project allows customization of dialogue generation techniques and strategies, enabling diverse conversational experiences.

## Installation

To install and set up the project, follow these steps:

1. Clone the project repository:

   ```shell
   git clone https://github.com/adityapujari98/AIConvoPlayground
   cd AIConvoPlayground

2. Set up the virtual environment (recommended):

    ```shell
   python3 -m venv venv
   source venv/bin/activate

3. Install the required dependencies:
   ```shell
   pip install -r requirements.txt

## Usage
To run the system, follow these steps:
1. Obtain an API key from OpenAI:
   
   - Visit the [OpenAI website](https://platform.openai.com/account/api-keys) to create an account and obtain an API key.

2. Configure the project:

   - If you want to use a locally hosted model, follow these steps:
     - Clone the repository for the gpt4all model:
       ```shell
       git clone https://github.com/your-username/gpt4-model.git
       cd gpt4-all-server
       ```
     - Set up the virtual environment (recommended):
       ```shell
       python3 -m venv venv
       source venv/bin/activate
       ```
     - Install the required dependencies:
       ```shell
       pip install -r requirements.txt
       ```
     - Start the model server:
       ```shell
       python app.py
       ```
     - Open the `model_api/model_urls.py` file in the AI Convo Playground project and add the model name and its access URL in the `model_urls` dictionary:
       ```python
       model_urls = {
           "Model_name": "http://localhost:{your-model-endpoint}",
       }
       ```
     - Make sure the gpt4all model server is running and accessible at the specified URL.

   Note: You need to clone the repository for the gpt4all model separately and ensure it is running before configuring the `model_urls.py` file in the AI Convo Playgroung project.

3. To run the project, execute the following command:
   ```shell
   streamlit run app.py
   ```

This command will initiate the conversation between the agents. You can observe the interactions between the agents in the console output. Feel free to modify the dialogue generation techniques, agent characters, or any other aspect of the project to suit your requirements.

## Contributing
Contributions to this project are welcome! If you have any ideas, suggestions, or bug reports, please submit them as issues or create a pull request with your proposed changes.

When contributing, please ensure that your code follows the existing coding style and conventions. Additionally, provide appropriate documentation and tests for the added features or bug fixes.

## License
This project is licensed under the MIT License. Feel free to use, modify, and distribute this code for both personal and commercial purposes.