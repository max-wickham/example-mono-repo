




<<<<<<< HEAD



compile-cpp-proto:
	protoc  -I=schemas/ --cpp_out=embedded/main/messages/  --plugin=protoc-gen-eams=protoc-gen-eams --eams_out=./embedded schemas/reading.proto
=======
run-data-stream:
	docker compose -f docker-compose.yml --profile "stream" up
build-data-stream:
	docker compose -f docker-compose.yml --profile "stream" build
>>>>>>> 9250c6b32fd16a93ef99b427d7dc1709755234c0
