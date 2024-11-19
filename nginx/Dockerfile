FROM nginx:1.19.0

ARG	NGINX_CONF_FILE=/etc/nginx/nginx.conf
ARG	HOST_HOSTNAME=$HOST_HOSTNAME

RUN	apt-get update && \
	apt-get install -y \
            bash \
			sed \
			openssl \
			curl

COPY ./nginx.conf $NGINX_CONF_FILE
RUN	sed 's/$HOST_HOSTNAME/'$HOST_HOSTNAME'/g' $NGINX_CONF_FILE > /tmp/conf && \
	mv /tmp/conf $NGINX_CONF_FILE

COPY . .
RUN chmod +x ./script.sh

CMD ["/bin/bash", "./script.sh"]
