FROM python:3.9-alpine3.17

COPY ./demo.py .
COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./demo.py"]
