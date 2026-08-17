# Sistema de pedidos

Este exemplo apresenta a infraestrutura de uma aplicacao de processamento de pedidos com Docker Compose. A base utiliza PostgreSQL para os dados da aplicacao e Redis para cache ou fila de tarefas. O Adminer pode ser ativado como ferramenta opcional para inspecionar o banco durante a demonstracao.

## Servicos de infraestrutura

| Servico | Funcao | Acesso entre containers |
|---|---|---|
| `db` | Persistencia dos pedidos em PostgreSQL | `db:5432` |
| `redis` | Cache e fila de processamento | `redis:6379` |
| `adminer` | Inspecao opcional do PostgreSQL | `db:5432` |

Os nomes `db` e `redis` sao resolvidos pelo DNS interno do Compose. Por isso, os consumidores nao devem usar IPs fixos nem `localhost` para acessar esses servicos.

## Configuracao

Crie o arquivo local de variaveis a partir do modelo:

```bash
cp .env.example .env
```

No PowerShell, use:

```powershell
Copy-Item .env.example .env
```

Antes de utilizar o ambiente fora de uma demonstracao local, substitua o valor de `POSTGRES_PASSWORD`. O arquivo `.env` nao deve ser versionado.

## Execucao da infraestrutura

Com Docker e o plugin Docker Compose instalados, execute:

```bash
docker compose up -d
docker compose ps
```

Para ativar tambem o Adminer:

```bash
docker compose --profile ferramentas up -d
```

Por padrao, o Adminer fica disponivel em `http://localhost:8081`. Na tela de conexao, o servidor deve ser `db`, e nao `localhost`.

## Persistencia

Os volumes nomeados `postgres_data` e `redis_data` preservam os dados quando os containers sao recriados. O comando a seguir encerra o ambiente sem remover os volumes:

```bash
docker compose down
```

Para remover deliberadamente os dados persistidos:

```bash
docker compose down -v
```

Na primeira criação do volume, o PostgreSQL executa o esquema disponível em `db/init`. A estrutura e os cuidados para recriá-la estão documentados em [docs/banco-de-dados.md](docs/banco-de-dados.md).

## Verificacao de saude

O PostgreSQL utiliza `pg_isready`, enquanto o Redis utiliza `redis-cli ping`. Esses testes permitem que os demais servicos aguardem dependencias realmente prontas, em vez de considerar apenas a ordem de criacao dos containers.

O estado pode ser consultado com:

```bash
docker compose ps
docker compose logs db redis
```

## Arquitetura completa

A descricao dos componentes da demonstracao e dos contratos para integracao com a aplicacao esta em [docs/arquitetura.md](docs/arquitetura.md).
