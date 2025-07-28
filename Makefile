# Makefile - Comandos útiles para Docker

.PHONY: build run stop clean logs shell

# Construir la imagen
build:
	docker-compose build

# Ejecutar la aplicación
run:
	docker-compose up -d

# Ejecutar en modo desarrollo (con logs visibles)
dev:
	docker-compose up

# Parar la aplicación
stop:
	docker-compose down

# Limpiar todo (contenedores + imágenes)
clean:
	docker-compose down -v --rmi all

# Ver logs
logs:
	docker-compose logs -f

# Entrar al contenedor
shell:
	docker-compose exec shopify-automation bash

# Reconstruir y ejecutar
rebuild:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d