FROM python:3.9.12

WORKDIR /inventory_management_bot

COPY ../inventory_management_bot/ .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./main.py"]