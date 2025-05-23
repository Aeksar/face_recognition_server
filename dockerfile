FROM python:3.12-slim

RUN apt-get update && apt-get install\
    libgl1\
    libgl1-mesa-glx \ 
    libglib2.0-0 -y && \
    rm -rf /var/lib/apt/lists/*
    
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY  . .

EXPOSE 8000

CMD ["python3", "main.py"]

