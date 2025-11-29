FROM python:3.11-slim

WORKDIR /norm-fullstack

COPY requirements.txt .

RUN pip uninstall -y llama-index llama-index-legacy || true && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade -r requirements.txt

ENV OPENAI_API_KEY=$OPENAI_API_KEY

COPY ./app /norm-fullstack/app
COPY ./docs /norm-fullstack/docs

RUN mkdir -p /norm-fullstack/data
RUN mkdir -p /norm-fullstack/uploads
RUN mkdir -p /norm-fullstack/qdrant_data

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
