


run-minio:
	docker compose -f docker-compose.yml up minio


run-data-ingest:
	docker compose -f docker-compose.yml --profile "ingest" up
	# --attach fake-data-gen

run-data-stream:
	docker compose -f docker-compose.yml --profile "stream" up
	# --attach fake-data-gen
stop-data-stream:
	docker compose -f docker-compose.yml --profile "stream" down
	# --attach fake-data-gen
build-data-stream:
	docker compose -f docker-compose.yml --profile "stream" build
