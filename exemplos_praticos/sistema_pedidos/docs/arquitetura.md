# Arquitetura do sistema de pedidos

## Objetivo

O exemplo representa um fluxo no qual um pedido é recebido por uma API, persistido no PostgreSQL e enviado para processamento assíncrono por meio do Redis. Um worker consome a tarefa e atualiza o estado do pedido. A documentação interativa do FastAPI permite criar e consultar pedidos pelo navegador.

```text
Navegador ou cliente HTTP -> API -> PostgreSQL
                                 -> Redis -> worker -> PostgreSQL
```

## Componentes implementados

| Componente | Responsabilidade | Dependências |
|---|---|---|
| API | Validar requisições, persistir pedidos e publicar tarefas | PostgreSQL e Redis |
| Worker | Consumir tarefas e atualizar pedidos | PostgreSQL e Redis |
| PostgreSQL | Armazenar pedidos e seus estados | Nenhuma |
| Redis | Disponibilizar a fila de tarefas | Nenhuma |
| Adminer | Permitir a inspeção opcional do PostgreSQL | PostgreSQL |

## Contrato de rede

Os componentes internos usam os nomes dos serviços como endereço:

- PostgreSQL: `db:5432`;
- Redis: `redis:6379`;
- API: `api:8000`.

A rede `backend` é marcada como interna para evitar acesso externo direto ao banco e ao Redis. API, worker, PostgreSQL e Redis participam dessa rede. O Adminer participa também da rede `ferramentas`, que permite publicar sua interface apenas em `127.0.0.1`. Assim, ele alcança o banco pelo nome `db`, sem tornar o PostgreSQL acessível diretamente pelo host.

A API também participa da rede `entrada`, pela qual sua porta é publicada somente em `127.0.0.1`. Ela funciona como limite entre os clientes externos e os serviços de dados.

## Contrato de inicializacao

A API e o worker dependem de `db` e `redis` com a condição `service_healthy`. A própria API possui um healthcheck em `GET /health`, que consulta as duas dependências. Essa configuração evita confundir container iniciado com serviço pronto para receber conexões.

O mecanismo melhora a inicialização local, mas não substitui o tratamento de falhas na aplicação. API e worker possuem tentativas limitadas de reconexão. Se o Redis falhar depois da persistência de um pedido e antes da publicação da tarefa, a API registra o pedido como `falhou` e devolve HTTP 503 com seu identificador.

## Persistencia

O volume `postgres_data` guarda os pedidos. O volume `redis_data` preserva a estrutura append-only do Redis, mas a fonte principal dos estados continua sendo o PostgreSQL. `docker compose down` preserva os volumes nomeados, enquanto `docker compose down -v` os remove deliberadamente.

## Variáveis usadas pela aplicação

A aplicação recebe as configurações por variáveis de ambiente, sem endereços ou credenciais fixados no código:

| Variável | Uso |
|---|---|
| `POSTGRES_DB` | Nome do banco |
| `POSTGRES_USER` | Usuário do PostgreSQL |
| `POSTGRES_PASSWORD` | Senha do PostgreSQL |
| `DATABASE_HOST` | Nome do serviço `db` |
| `REDIS_HOST` | Nome do serviço `redis` |

As credenciais presentes em `.env.example` são apenas valores demonstrativos. Credenciais reais e o arquivo `.env` local não devem ser enviados ao repositório.
