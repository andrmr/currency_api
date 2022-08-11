FROM python:3.10
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
ENV UVICORN_PORT 8080
CMD uvicorn main:app --proxy-headers --host "0.0.0.0" --port $UVICORN_PORT