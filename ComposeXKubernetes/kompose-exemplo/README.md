# Exemplo simples de Kompose

Este exemplo mostra a mesma aplicação em três momentos:

```text
compose.yaml --(docker compose)--> contêiner local
     |
     +--------(kompose convert)--> Deployment + Service
                                      |
                                      +--(kubectl apply)--> Kubernetes
```

A aplicação é apenas a página padrão do Nginx.

## Arquivos

- `compose.yaml`: entrada usada pelo Docker Compose e pelo Kompose;
- `manifestos-referencia/web-deployment.yaml`: equivalente Kubernetes didático;
- `manifestos-referencia/web-service.yaml`: equivalente Kubernetes didático;
- `verificar-ambiente.sh`: verifica se as ferramentas necessárias estão no PATH.

Os manifestos de referência foram escritos para estudo. A saída real do
Kompose pode ter labels, anotações, ordem e nomes de arquivo diferentes conforme
a versão.

## Facilitando sua experiência: Makefile

Execute `make ajuda` para ver todos os comandos. O fluxo da demonstração é:

```bash
make verificar
make compose
make testar-compose
make parar-compose
make kubernetes
make testar-kubernetes
make escalar
make limpar
```

Os comandos detalhados abaixo continuam disponíveis para explicar o que cada
etapa faz.

## 1. Verificar as ferramentas

```bash
bash verificar-ambiente.sh
```

## 2. Executar com Docker Compose

```bash
docker compose config
docker compose up -d
docker compose ps
curl http://localhost:8080
docker compose down
```

## 3. Converter com Kompose

Crie uma pasta separada para não misturar a saída com os arquivos de estudo:

```bash
mkdir -p kubernetes-gerado
cd kubernetes-gerado
kompose -f ../compose.yaml convert
ls -1
```

Normalmente serão gerados um arquivo de Deployment e um de Service.

## 4. Executar no Minikube

Ainda dentro de `kubernetes-gerado`:

```bash
minikube start
kubectl apply -f .
kubectl get deployments,pods,services
kubectl rollout status deployment/web
minikube service web --url
```

Abra em outro terminal o endereço retornado pelo último comando, ou use:

```bash
curl "ENDERECO_RETORNADO"
```

## 5. Mostrar a escala

```bash
kubectl scale deployment web --replicas=3
kubectl get pods
```

O Deployment passa a desejar três réplicas, e o controlador cria Pods até
atingir esse estado.

## 6. Limpar ao terminar

```bash
kubectl delete -f .
minikube stop
```

Para excluir completamente o cluster local, opcionalmente:

```bash
minikube delete
```
