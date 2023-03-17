# Bissmillahirrahmanirraheem

FROM python:3.10

ENV PYTHONUNBUPYTHONUNBUFFERED="TRUE"
ENV PORT=8000

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app

COPY . .

RUN /root/.local/bin/poetry config virtualenvs.create false && /root/.local/bin/poetry install --no-dev

CMD alembic upgrade head && uvicorn app.main:app --port $PORT --host 0.0.0.0

