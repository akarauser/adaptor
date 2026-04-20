# adaptor
Local Thinking Bot

Local and private thinking chatbot with history and long term memory. You can keep track of thinking phase under Thinking part of the GUI. You can move around your previous conversations and continue from where you left of. You can easily change the model you have chose without interacting with code.

## Overview
- Local usage: You can use your model without internet connection with your local system.
- User system: You can sign up and sign in to your local accounts.
- Chat history: System saves every conversation locally as sql database file.
- Long term memory: Model will remember and continue conversations from history and within the session.
- Vision: You can interact with your images over the chat.
- Model selection: You can interactively change the model you use for the chat.

## Installation
* Application needs Docker. You can follow the steps from [Get Docker.](https://docs.docker.com/get-started/introduction/get-docker-desktop/)

* Install application
```
git clone https://github.com/akarauser/adaptor.git
cd adaptor

docker compose up
```

## Usage
* Pull Ollama model (Only for first time):
> docker exec -it ollama_adaptor ollama pull qwen3.5:4b

*You can pull another model with vision abilities instead qwen3.5:4b if you want the vision system. Else, you can use non-thinking, non-vision models too.*

* Go to http://localhost:8501/

##  License
MIT License (see LICENSE)

## Project Structure
```
adaptor
├── .dockerignore
├── .gitignore
├── .python-version
├── adaptor
│   ├── .streamlit
│   │   └── config.toml
│   ├── main.py
│   ├── scripts
│   │   ├── user.py
│   │   ├── utils.py
│   │   └── __init__.py
│   ├── main.py
│   └── __init__.py
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── README.md
├── tests
│   ├── test_main.py
│   └── __init__.py
└── uv.lock
```
