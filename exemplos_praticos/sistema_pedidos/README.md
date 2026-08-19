# Sistema de pedidos

Este exemplo apresenta uma aplicacao de processamento de pedidos com Docker Compose. A API recebe pedidos e os persiste no PostgreSQL, publicando uma tarefa no Redis somente apos a confirmacao da escrita. O worker consome essa fila e atualiza o estado do pedido. O Adminer pode ser ativado como ferramenta opcional para inspecionar o banco durante a demonstracao.

## Servicos

| Servico | Funcao | Acesso entre containers |
|---|---|---|
| `db` | Persistencia dos pedidos em PostgreSQL | `db:5432` |
| `redis` | Fila de tarefas de processamento | `redis:6379` |
| `api` | Cria e consulta pedidos, publica tarefas na fila | `api:8000` |
| `worker` | Consome a fila e atualiza o estado dos pedidos | Nenhum (nao expoe porta) |
| `adminer` | Inspecao opcional do PostgreSQL | `db:5432` |

Os nomes `db`, `redis` e `api` sao resolvidos pelo DNS interno do Compose. Por isso, os consumidores nao devem usar IPs fixos nem `localhost` para acessar esses servicos. A API e o worker recebem `DATABASE_HOST=db` e `REDIS_HOST=redis` pelo proprio `compose.yaml`, nunca fixados no codigo.

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

## Uso da API

Por padrao, a API fica disponivel em `http://127.0.0.1:8000` (porta definida por `API_PORT` no `.env`).

Criar um pedido:

```bash
curl -X POST http://127.0.0.1:8000/pedidos \
  -H "Content-Type: application/json" \
  -d '{"cliente": "Ana", "descricao": "Duas pizzas"}'
```

Listar pedidos:

```bash
curl http://127.0.0.1:8000/pedidos
```

Consultar um pedido especifico:

```bash
curl http://127.0.0.1:8000/pedidos/1
```

O pedido e criado com o estado `pendente` e publicado na fila `fila:pedidos` do Redis somente depois do commit no PostgreSQL. O worker consome essa fila com `BRPOP`, movendo o pedido para `processando` e, em seguida, para `processado` (com `processado_em` preenchido) ou `falhou`. O acompanhamento pode ser feito com:

```bash
docker compose logs -f worker
```

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

O PostgreSQL utiliza `pg_isready`, o Redis utiliza `redis-cli ping`, e a API utiliza `curl` sobre `GET /health`, que verifica de fato a conexao com o PostgreSQL e o Redis (nao apenas se o processo esta em execucao). Esses testes permitem que os demais servicos aguardem dependencias realmente prontas, em vez de considerar apenas a ordem de criacao dos containers. O worker e o Adminer dependem de `db` e `redis` com a condicao `service_healthy`.

O estado pode ser consultado com:

```bash
docker compose ps
docker compose logs db redis api
```

Os procedimentos usados para conferir redes, acesso ao Adminer, descoberta de serviços e persistência estão em [docs/validacao-infraestrutura.md](docs/validacao-infraestrutura.md).

## Arquitetura completa

A descricao dos componentes da demonstracao e dos contratos para integracao com a aplicacao esta em [docs/arquitetura.md](docs/arquitetura.md).
