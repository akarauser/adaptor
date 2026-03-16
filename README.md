# adaptor
Local Thinking Bot

Local and private thinking chatbot with history and long term memory. You can keep track of thinking phase under Thinking part of the GUI. You can move around your previous conversations and continue from where you left of. You can easily change the model you have chose without interacting with code.

## Overview
- Local usage: You can use your model without internet connection with your local system
- Chat history: System saves every conversation locally as sql database file
- Long term memory: Model will remember and continue conversations from history and within the session

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

*You can pull another thinking model with vision abilities instead qwen3.5:4b. If you have pulled another model, make sure to update adaptor/adaptor/data/config.json file from inside the container.*

* Go to http://localhost:8501/

*You can start new conversation by basically refreshing the page.*

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
│   ├── data
│   │   └── config.json
│   ├── main.py
│   ├── scripts
│   │   ├── utils.py
│   │   └── __init__.py
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
