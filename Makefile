REGISTRY ?= newwayland
BIN ?= baseline-economy
PKG := github.com/${REGISTRY}/${BIN}
VERSION ?= $(shell git log -1 --format="%h")

container:
	docker build -t ${REGISTRY}/${BIN}:${VERSION} .

push: container
	docker push ${REGISTRY}/${BIN}:${VERSION}

run: container
	docker run -it -p 8521:8521 --name test-${BIN} ${REGISTRY}/${BIN}:${VERSION}
