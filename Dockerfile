FROM python:3.14.5-alpine3.22

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt

COPY ./src ./src

ENV ENV="prod"
ENV LOG_LEVEL="INFO"

ENTRYPOINT ["python", "src/main.py"]