FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y bash

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN chmod +x script.sh

RUN useradd -ms /bin/bash mail_service_user
RUN chown -R mail_service_user:mail_service_user /app/mail_service/

USER mail_service_user

EXPOSE 8000

CMD ["/bin/bash", "./script.sh"]