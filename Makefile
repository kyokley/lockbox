.PHONY: build build-dev publish

build:
	docker build -t kyokley/lockbox .

build-dev:
	docker build --build-arg REQS= -t kyokley/lockbox .

shell: build-dev
	docker run --rm -it -v $$HOME/.gnupg:/root/.gnupg -u $$UID:$$GID --entrypoint /bin/bash kyokley/lockbox

publish: build
	docker push kyokley/lockbox
