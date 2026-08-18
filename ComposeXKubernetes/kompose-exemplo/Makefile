SHELL := /usr/bin/env bash
.DEFAULT_GOAL := ajuda

K8S_DIR := kubernetes-gerado

.PHONY: ajuda verificar validar compose testar-compose parar-compose converter \
	minikube kubernetes testar-kubernetes escalar status limpar

ajuda:
	@printf '%s\n' \
		'make verificar           Verifica as ferramentas' \
		'make validar             Valida o compose.yaml' \
		'make compose             Inicia o Nginx com Docker Compose' \
		'make testar-compose      Testa http://localhost:8080' \
		'make parar-compose       Encerra o Docker Compose' \
		'make converter           Gera os manifestos com Kompose' \
		'make minikube            Inicia o cluster local' \
		'make kubernetes          Converte e aplica no Minikube' \
		'make testar-kubernetes   Testa o NodePort 30080' \
		'make escalar             Altera o Deployment para 3 réplicas' \
		'make status              Mostra o estado dos serviços' \
		'make limpar              Remove os recursos e para o Minikube'

verificar:
	bash verificar-ambiente.sh

validar:
	docker compose config >/dev/null
	@echo '[OK] compose.yaml válido.'

compose: validar
	docker compose up -d --wait
	docker compose ps

testar-compose:
	@curl --fail --silent --show-error http://localhost:8080/ -o /dev/null
	@echo '[OK] Compose respondeu em http://localhost:8080.'

parar-compose:
	docker compose down

converter:
	mkdir -p $(K8S_DIR)
	kompose -f compose.yaml convert -o $(K8S_DIR)
	@ls -1 $(K8S_DIR)

minikube:
	@if minikube status >/dev/null 2>&1; then \
		echo '[OK] Minikube já está em execução.'; \
	else \
		minikube start; \
	fi

kubernetes: converter minikube
	kubectl apply -f $(K8S_DIR)
	kubectl rollout status deployment/web --timeout=120s
	kubectl get deployments,pods,services

testar-kubernetes:
	@url="http://$$(minikube ip):30080"; \
		curl --fail --silent --show-error --retry 10 --retry-connrefused \
			--retry-delay 1 "$$url" -o /dev/null && \
		echo "[OK] Kubernetes respondeu em $$url."

escalar:
	kubectl scale deployment/web --replicas=3
	kubectl rollout status deployment/web --timeout=120s
	kubectl get pods

status:
	docker compose ps
	minikube status
	kubectl get deployments,pods,services

limpar:
	-docker compose down
	-kubectl delete -f $(K8S_DIR) --ignore-not-found=true
	-minikube stop
