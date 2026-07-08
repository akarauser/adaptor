FROM python:3.12-slim

WORKDIR /adaptor

RUN apt-get update && apt-get install -y --no-install-recommends curl

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY . /adaptor

RUN uv sync --locked

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["uv", "run", "streamlit", "run", "adaptor/main.py", "--server.port=8501", "--server.address=0.0.0.0"]