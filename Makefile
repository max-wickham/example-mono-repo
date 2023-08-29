




run-data-stream:
	docker compose -f docker-compose.yml --profile "stream" up
build-data-stream:
	docker compose -f docker-compose.yml --profile "stream" build
