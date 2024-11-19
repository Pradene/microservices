FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y \
                    bash \
                    curl

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN chmod +x script.sh

RUN useradd -ms /bin/bash chat_service_user
RUN chown -R chat_service_user:chat_service_user /app/chat_service/

USER chat_service_user

EXPOSE 8000

CMD ["/bin/bash", "./script.sh"]
