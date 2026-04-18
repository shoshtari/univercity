FROM python:3.12-slim

WORKDIR /app
COPY ./requirements.txt .

RUN pip config set global.index-url https://pypi.devneeds.ir/simple/
RUN pip install -r requirements.txt --retries 4

COPY . .

CMD ["python", "main.py", "runserver"]
