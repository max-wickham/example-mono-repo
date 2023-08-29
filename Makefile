







compile-cpp-proto:
	protoc  -I=schemas/ --cpp_out=embedded/main/messages/  --plugin=protoc-gen-eams=protoc-gen-eams --eams_out=./embedded schemas/reading.proto
