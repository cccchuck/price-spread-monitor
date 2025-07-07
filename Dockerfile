FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml ./
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]