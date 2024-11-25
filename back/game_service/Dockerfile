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

RUN useradd -ms /bin/bash game_service_user
RUN chown -R game_service_user:game_service_user /app/game_service/

USER game_service_user

EXPOSE 8000

CMD ["/bin/bash", "./script.sh"]