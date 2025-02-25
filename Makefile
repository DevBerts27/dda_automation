# Nome do aplicativo e versão
IMAGE_NAME := dda_auto
CONTAINER_NAME := dda

# A imagem final vai se chamar: seu-registry.com/usuario/meu_app:1.0.0

# ----- Comandos padrão ----

.PHONY: build run stop push clean

## Executa o container em background
run: build
	docker run --rm -t --name $(CONTAINER_NAME) -v /mnt/m:/Agenda $(IMAGE_NAME)

start: build
	docker start $(CONTAINER_NAME)

## Build da imagem Docker
build: remove_image
	docker build -t $(IMAGE_NAME) .

## Para o container
stop:
	docker stop $(CONTAINER_NAME) || true

## Remove o container
remove_container: stop
	docker rm $(CONTAINER_NAME) || true

## Remove a imagem
remove_image: remove_container
	docker rmi $(IMAGE_NAME) || true
