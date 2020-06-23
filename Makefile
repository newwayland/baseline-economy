REGISTRY ?= newwayland
BIN ?= baseline-economy
PKG := github.com/${REGISTRY}/${BIN}
VERSION ?= $(shell git log -1 --format="%h")

container:
	docker build -t ${REGISTRY}/${BIN}:${VERSION} .

push: container
	docker push ${REGISTRY}/${BIN}:${VERSION}

run: container
	docker run --rm -it -p 8521:8521 --name test-${BIN} ${REGISTRY}/${BIN}:${VERSION}

k8s_push_deploy: push k8s_deploy

k8s_deploy:
	sh create_kustomize.sh ${REGISTRY}/${BIN} ${VERSION}
	kubectl apply -k k8s

k8s_delete:
	kubectl delete -k k8s
