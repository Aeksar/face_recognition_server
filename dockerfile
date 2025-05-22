FROM python:3.12-slim

RUN apt update && apt-get install -y libglib2.0-0 libsm6 libxrender1 libxext6

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY  . .

EXPOSE 8000

CMD ["python3", "main.py"]

