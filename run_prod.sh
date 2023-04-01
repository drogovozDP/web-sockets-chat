#!/bin/bash

docker compose --env-file=./backend/.env -f docker-compose-prod.yml up --build
