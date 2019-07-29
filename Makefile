.PHONY: build build-dev publish

build:
	docker build -t kyokley/lockbox .

build-dev:
	docker build --build-arg REQS= -t kyokley/lockbox .

publish: build
	docker push kyokley/lockbox
