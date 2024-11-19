FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y bash

RUN useradd -ms /bin/bash notification_service_user

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN chmod +x script.sh

EXPOSE 8000

USER notification_service_user

CMD ["/bin/bash", "./script.sh"]