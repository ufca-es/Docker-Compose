# Arquitetura do sistema de pedidos

## Objetivo

O exemplo representa um fluxo no qual um pedido e recebido por uma API, persistido no PostgreSQL e enviado para processamento assincrono por meio do Redis. Um worker consome a tarefa e atualiza o estado do pedido. Uma interface web permite criar e consultar pedidos.

```text
Navegador -> frontend -> API -> PostgreSQL
                             -> Redis -> worker -> PostgreSQL
```

## Componentes previstos

| Componente | Responsabilidade | Dependencias |
|---|---|---|
| Frontend | Criar e consultar pedidos | API |
| API | Validar requisicoes, persistir pedidos e publicar tarefas | PostgreSQL e Redis |
| Worker | Consumir tarefas e atualizar pedidos | PostgreSQL e Redis |
| PostgreSQL | Armazenar pedidos e seus estados | Nenhuma |
| Redis | Disponibilizar a fila de tarefas | Nenhuma |

## Contrato de rede

Os componentes internos devem usar os nomes dos servicos como endereco:

- PostgreSQL: `db:5432`;
- Redis: `redis:6379`;
- API: `api:8000`.

A rede `backend` e marcada como interna para evitar acesso externo direto ao banco e ao Redis. Na integracao da aplicacao, uma segunda rede deve conectar somente o frontend e a API. A API participa das duas redes e funciona como limite entre a entrada da aplicacao e os servicos de dados.

## Contrato de inicializacao

A API e o worker devem depender de `db` e `redis` com a condicao `service_healthy`. O frontend deve depender do healthcheck da API. Essa configuracao evita confundir container iniciado com servico pronto para receber conexoes.

O mecanismo melhora a inicializacao local, mas nao substitui tratamento de falhas na aplicacao. API e worker ainda devem possuir tentativas limitadas de reconexao e mensagens de erro claras caso uma dependencia fique indisponivel depois da inicializacao.

## Persistencia

O volume `postgres_data` guarda os pedidos. O volume `redis_data` preserva a estrutura append-only do Redis, mas a fonte principal dos estados continua sendo o PostgreSQL. A demonstracao de persistencia deve comparar `docker compose down` com `docker compose down -v`, explicando que apenas o segundo remove os volumes nomeados.

## Variaveis esperadas pela aplicacao

A aplicacao deve receber as configuracoes por variaveis de ambiente, sem enderecos ou credenciais fixados no codigo:

| Variavel | Uso esperado |
|---|---|
| `POSTGRES_DB` | Nome do banco |
| `POSTGRES_USER` | Usuario do PostgreSQL |
| `POSTGRES_PASSWORD` | Senha do PostgreSQL |
| `DATABASE_HOST` | Nome do servico `db` |
| `REDIS_HOST` | Nome do servico `redis` |

As credenciais presentes em `.env.example` sao apenas valores demonstrativos. Credenciais reais e o arquivo `.env` local nao devem ser enviados ao repositorio.
