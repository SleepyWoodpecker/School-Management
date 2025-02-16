# install image and dependencies first, to prevent hash invalidation of dependencies when source code changes
FROM python:3.10-slim

COPY requirements.txt .

RUN pip install -r requirements.txt
RUN pip install fastapi uvicorn

COPY ./src ./src

WORKDIR /src

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3003", "--root-path", "/api/v1"]