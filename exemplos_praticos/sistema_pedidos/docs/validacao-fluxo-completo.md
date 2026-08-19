# Validação do fluxo completo

Este procedimento valida a integração entre API, PostgreSQL, Redis e worker. Os comandos devem ser executados no diretório `exemplos_praticos/sistema_pedidos`, depois da criação do arquivo `.env`.

## Inicialização

Construa as imagens, inicie os serviços e aguarde os healthchecks:

```bash
docker compose up -d --build --wait
docker compose ps
```

PostgreSQL, Redis e API devem aparecer como `healthy`. O worker deve aparecer como `Up`, pois não expõe uma rota HTTP e não possui healthcheck próprio.

Consulte a saúde da API:

```bash
curl http://127.0.0.1:8000/health
```

Resultado esperado:

```json
{"status":"ok","dependencias":{"postgres":"ok","redis":"ok"}}
```

## Criação e processamento

Crie um pedido:

```bash
curl -X POST http://127.0.0.1:8000/pedidos \
  -H "Content-Type: application/json" \
  -d '{"cliente":"Ana","descricao":"Pedido de demonstracao"}'
```

A resposta inicial possui estado `pendente`. Depois de aproximadamente um segundo, consulte o identificador retornado:

```bash
curl http://127.0.0.1:8000/pedidos/1
```

O estado deve mudar para `processado`, com `processado_em` preenchido. O processamento também pode ser acompanhado com:

```bash
docker compose logs -f worker
```

## Inspeção dos serviços

Confira diretamente o banco:

```bash
docker compose exec db psql -U compose -d pedidos -c \
  "SELECT id, cliente, status, processado_em FROM pedidos ORDER BY id;"
```

Confira o tamanho da fila:

```bash
docker compose exec redis redis-cli LLEN fila:pedidos
```

Depois que o worker termina, a fila deve possuir tamanho zero.

## Falha controlada do Redis

Para demonstrar o tratamento de indisponibilidade, pare o Redis e tente criar outro pedido:

```bash
docker compose stop redis
```

A API deve responder HTTP 503. O corpo informa `pedido_id` e estado `falhou`, evitando que o registro permaneça indefinidamente como `pendente` sem uma tarefa na fila.

Reative o Redis:

```bash
docker compose start redis
```

Depois que o serviço voltar ao estado saudável, `GET /health` deve retornar `status: ok` novamente.

## Resultados verificados

Em 19 de agosto de 2026, com Docker Engine 29.7.2 e Docker Compose 5.3.1:

- todas as imagens foram construídas;
- PostgreSQL, Redis e API atingiram o estado `healthy`;
- a API criou um pedido como `pendente`;
- o worker consumiu a tarefa e alterou o pedido para `processado`;
- `processado_em` foi preenchido;
- a fila ficou vazia depois do consumo;
- consultas inexistentes retornaram HTTP 404;
- entradas inválidas retornaram HTTP 422;
- o pedido permaneceu após `down/up` sem remoção dos volumes;
- com o Redis parado, a API retornou HTTP 503 e registrou o pedido como `falhou`;
- não restaram pedidos `pendente` sem tarefa após a falha;
- a API recuperou a saúde depois do retorno do Redis.

Os registros criados especificamente durante a validação foram removidos ao final dos testes.
