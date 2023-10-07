run-data-stream:
	docker compose -f docker-compose.yml --profile "stream" up
build-data-stream:
	docker compose -f docker-compose.yml --profile "stream" build


run-backend:
	docker compose -f docker-compose.yml --profile "backendfull" up
build-backend:
	docker compose -f docker-compose.yml --profile "backendfull" build
