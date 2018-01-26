default: build
	$(MAKE) run

run:
	docker run --rm -p 8000:8000 --name jticker -v "$${PWD}:/ticker/" ticker

build:
	docker build -t ticker .


.PHONY: default build run
