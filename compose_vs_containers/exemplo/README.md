# Exemplo prático: Compose vs. Containers

Esta é uma aplicação simples em **Flask** que se conecta a um **Redis** e conta quantas vezes a rota `/` foi acessada. O objetivo é demonstrar, na prática, a diferença entre subir esse ambiente usando apenas containers (`docker run`) e usando o **Docker Compose**.

## Estrutura do projeto

```
exemplo/
├── app.py               # Aplicação Flask
├── requirements.txt     # Dependências Python
├── Dockerfile           # Imagem da aplicação
├── compose.yml          # Orquestração dos serviços (app + redis)
└── README.md
```

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) instalado
- Docker Compose (já incluso no Docker Desktop e nas versões recentes do Docker Engine, via `docker compose`)

---

## Opção 1 - Rodando com Docker Compose (recomendado)

Com o Docker Compose, toda a aplicação (Flask + Redis) sobe com **um único comando**, pois a configuração já está declarada no `docker-compose.yml`.

```bash
cd exemplo

# Sobe os dois serviços (app e redis) em segundo plano
docker compose up -d --build

# Ver os logs
docker compose logs -f

# Parar e remover os containers e a rede criados
docker compose down
```

Depois de subir, acesse:

```
http://localhost:5000
```

Cada vez que você atualizar a página, o contador `total_de_acessos` deve aumentar- isso mostra que a aplicação está persistindo o estado no Redis.

### Por que isso é mais simples?

O Compose cuidou automaticamente de:
- Criar uma rede para os dois serviços se comunicarem;
- Resolver o serviço `redis` pelo nome (usado na variável `REDIS_HOST=redis`);
- Definir a ordem de inicialização (`depends_on`);
- Buildar a imagem da aplicação a partir do `Dockerfile`.

---

## Opção 2 - Rodando manualmente com `docker run` (sem Compose)

Para fins de comparação, é possível recriar o mesmo ambiente usando apenas comandos `docker`, sem o Compose. Note como o número de passos e a chance de erro aumentam:

```bash
cd exemplo

# 1. Criar uma rede para os containers se comunicarem
docker network create rede-exemplo

# 2. Subir o Redis manualmente, conectado à rede
docker run -d --name redis --network rede-exemplo redis:7-alpine

# 3. Buildar a imagem da aplicação
docker build -t app-exemplo .

# 4. Subir a aplicação, informando manualmente o host do Redis
docker run -d --name app --network rede-exemplo \
  -e REDIS_HOST=redis -e REDIS_PORT=6379 \
  -p 5000:5000 app-exemplo
```

Acesse também em:

```
http://localhost:5000
```

Para derrubar tudo manualmente:

```bash
docker stop app redis
docker rm app redis
docker network rm rede-exemplo
```

---

## Comparando as duas abordagens

| Passo                                   | `docker run`                        | Docker Compose        |
|--------------------------------------------|------------------------------------------|--------------------------|
| Criar rede                               | Manual (`docker network create`)     | Automático              |
| Subir Redis                              | 1 comando                            | Declarado no YAML       |
| Buildar e subir a aplicação              | 2 comandos                           | Declarado no YAML       |
| Conectar app ao Redis                    | Variáveis de ambiente na mão          | Já configurado          |
| Subir tudo                               | 4 comandos, em ordem específica       | `docker compose up -d` |
| Derrubar tudo                            | 3 comandos                            | `docker compose down`  |

Esse exemplo evidencia, na prática, o que é discutido no arquivo [`compose_vs_containers.md`](../compose_vs_containers.md): o Compose não substitui os containers, mas simplifica drasticamente a orquestração de múltiplos serviços.

---

## Endpoints disponíveis

| Rota      | Descrição                                   |
|-----------|-----------------------------------------------|
| `/`       | Incrementa e retorna o contador de acessos     |
| `/health` | Verifica se a aplicação está no ar (`status: ok`) |
