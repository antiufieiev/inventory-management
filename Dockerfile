FROM python:3.9-alpine3.17

WORKDIR /inventory_management_bot

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./main.py"]