NAME			:= Transcendence
DOCKER_FLAGS 	:= --build
HOST_HOSTNAME	:= $(shell hostname)
DIR				:= $(shell basename $(shell pwd))

ifneq ($(fg),)
	DOCKER_FLAGS += -d
endif

all: ${NAME}

${NAME}:
	HOST_HOSTNAME=$(HOST_HOSTNAME) docker compose build --parallel
	HOST_HOSTNAME=$(HOST_HOSTNAME) docker compose up

up:
	docker compose up -d

down:
	docker compose down

clean:
	-docker container prune -f
	-docker rmi $(docker images)

re: down clean
	-docker volume prune -f
	${MAKE} ${NAME}