FROM python:3.10-alpine

WORKDIR /app

COPY src/requirements.txt .

RUN pip install -r requirements.txt

COPY src/app .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
