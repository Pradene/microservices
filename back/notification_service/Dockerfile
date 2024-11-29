FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y bash

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN chmod +x script.sh

EXPOSE 8000

CMD ["/bin/bash", "./script.sh"]