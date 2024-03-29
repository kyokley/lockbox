.PHONY: build build-dev publish

build:
	docker build --target final -t kyokley/lockbox .

build-dev:
	docker build --target dev -t kyokley/lockbox .

publish: build
	docker push kyokley/lockbox

shell:
	docker run --rm -it --entrypoint /bin/bash -v $$(pwd):/code kyokley/lockbox

tests: build-dev
	docker run --rm -t --entrypoint pytest -v $$(pwd):/code --workdir /code kyokley/lockbox
