# Validação da infraestrutura

Este procedimento verifica a configuração do Compose sem depender da API ou do worker. Os comandos devem ser executados no diretório `exemplos_praticos/sistema_pedidos`, depois da criação do arquivo `.env`.

## Configuração resolvida

Antes de criar containers, valide a interpolação das variáveis e a estrutura do arquivo:

```bash
docker compose config --quiet
```

Ausência de saída e código de término zero indicam que o Compose aceitou a configuração. Esse teste não garante que as imagens iniciem corretamente.

## Healthchecks

Inicie somente os serviços principais e aguarde os healthchecks:

```bash
docker compose up -d --wait
docker compose ps
```

Os serviços `db` e `redis` devem aparecer como `healthy`. Também é possível executar diretamente os mesmos mecanismos usados pelos healthchecks:

```bash
docker compose exec db pg_isready -U compose -d pedidos
docker compose exec redis redis-cli ping
```

O Redis deve responder `PONG`, e o PostgreSQL deve informar que está aceitando conexões.

## Descoberta por nome de serviço

O Adminer acessa o PostgreSQL pelo endereço `db:5432`. O nome `db` é resolvido pelo DNS interno do Compose e substitui a descoberta manual de endereços IP.

Ative o perfil opcional:

```bash
docker compose --profile ferramentas up -d --wait
```

Abra `http://127.0.0.1:8081` e use os seguintes dados:

| Campo | Valor padrão |
|---|---|
| Sistema | PostgreSQL |
| Servidor | `db` |
| Usuário | `compose` |
| Senha | valor de `POSTGRES_PASSWORD` no `.env` |
| Base de dados | `pedidos` |

O Adminer participa de duas redes. A rede `backend` permite alcançar o banco, enquanto `ferramentas` permite publicar sua interface em `127.0.0.1`. PostgreSQL e Redis permanecem apenas na rede interna e não publicam portas no host.

## Persistência do Redis

Grave uma chave temporária:

```bash
docker compose exec redis redis-cli SET validacao:persistencia confirmado
```

Recrie os containers sem remover os volumes e consulte a chave:

```bash
docker compose down
docker compose up -d --wait
docker compose exec redis redis-cli GET validacao:persistencia
```

O resultado esperado é `confirmado`. Remova a chave usada no teste:

```bash
docker compose exec redis redis-cli DEL validacao:persistencia
```

## Resultados observados

Em 17 de agosto de 2026, com Docker Engine 29.7.2 e Docker Compose 5.3.1:

- PostgreSQL e Redis atingiram o estado `healthy`;
- o Redis respondeu `PONG`;
- o Adminer respondeu HTTP 200 em `127.0.0.1:8081`;
- a porta do Adminer apareceu como `127.0.0.1:8081->8080/tcp`;
- PostgreSQL e Redis não publicaram portas no host;
- a chave `validacao:persistencia` permaneceu após `down/up`;
- a chave temporária foi removida e os containers foram encerrados ao final.

Esses resultados confirmam a infraestrutura local testada, mas ainda não validam o fluxo completo de pedidos, que depende da integração posterior da API e do worker.
