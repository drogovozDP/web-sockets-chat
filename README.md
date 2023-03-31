# web-sockets-chat

## Intro
This application is a simple chat that uses WebSocket protocol to propagate messages among users.
Server has WebSocket connection manager that sends messages only to online users.

## Run
1. To be able to run this application, you need to install `Docker` (and `docker compose`, if you install it separately). Navigate to [official site](https://www.docker.com/) to install `Docker`.
2. Create environment variables in the `backend` and `frontend` directories. In those directories you can find `.env-example` files. For simplicity, you can just copy the content of `.env-example` file and paste it to `.env` file in the `backend` and `frontend` directories respectively.

You can run this application in two ways: `develop` and `production`. Navigate to the appropriate for you section.


### Develop
Run the following command in the root directory to start `develop` version:

`docker-compose --env-file=./backend/.env up --build`

### Production
Run the following command in the root directory to start `production` version:

`docker-compose -f docker-compose-prod.yml --env-file=./backend/.env up --build`
