# Banco de dados do sistema de pedidos

## Inicialização automática

O diretório `db/init` é montado em `/docker-entrypoint-initdb.d` no container do PostgreSQL. A imagem oficial executa os arquivos desse diretório em ordem alfabética somente quando o volume de dados está vazio.

O script `001_schema.sql` cria a tabela `pedidos` e um índice para consultas por estado. O identificador usa uma sequência gerenciada pelo PostgreSQL, permitindo que a aplicação obtenha um novo ID sem coordenar valores entre processos.

## Estrutura da tabela

| Campo | Tipo | Finalidade |
|---|---|---|
| `id` | `BIGSERIAL` | Identificador do pedido |
| `cliente` | `VARCHAR(120)` | Nome informado na criação |
| `descricao` | `TEXT` | Conteúdo do pedido |
| `status` | `VARCHAR(20)` | Estado atual do processamento |
| `criado_em` | `TIMESTAMPTZ` | Momento de criação |
| `processado_em` | `TIMESTAMPTZ` | Momento em que o processamento terminou |

Os estados aceitos são `pendente`, `processando`, `processado` e `falhou`. Uma restrição impede valores diferentes desses. Outra restrição evita registrar `processado_em` enquanto o pedido ainda não possui o estado `processado`.

## Recriação durante o desenvolvimento

Alterar o script depois da primeira inicialização não modifica automaticamente um banco já persistido. Para reconstruir o ambiente local e executar novamente os scripts, remova deliberadamente os volumes:

```bash
docker compose down -v
docker compose up -d
```

Esse procedimento apaga os pedidos existentes e deve ser usado apenas quando a perda dos dados locais for aceitável. Em sistemas reais, mudanças posteriores no esquema exigiriam uma ferramenta de migração, em vez da remoção do banco.

## Consultas de verificação

Depois que o container estiver saudável, a tabela pode ser conferida sem instalar o cliente PostgreSQL na máquina hospedeira:

```bash
docker compose exec db psql -U compose -d pedidos -c "\d pedidos"
```

Para listar os pedidos:

```bash
docker compose exec db psql -U compose -d pedidos -c "SELECT * FROM pedidos ORDER BY id;"
```

Os comandos usam os valores fornecidos em `.env.example`. Caso `POSTGRES_USER` ou `POSTGRES_DB` sejam alterados no arquivo `.env`, os argumentos `-U` e `-d` também precisam ser ajustados.

## Resultados verificados

Em 17 de agosto de 2026, o ambiente foi validado com Docker Engine 29.7.2 e Docker Compose 5.3.1. Foram observados os seguintes resultados:

- `docker compose config --quiet` aceitou a configuração;
- PostgreSQL e Redis atingiram o estado `healthy`;
- o script criou a tabela, a chave primária, o índice e as duas restrições esperadas;
- um pedido sem estado explícito recebeu o valor padrão `pendente`;
- o PostgreSQL rejeitou o estado `desconhecido` pela restrição `pedidos_status_valido`;
- o pedido de teste permaneceu após `docker compose down` e uma nova execução de `docker compose up -d --wait`;
- o registro usado na validação foi removido ao final, e os containers foram encerrados sem excluir os volumes.

O perfil opcional do Adminer e a integração com API e worker não fazem parte desta validação do esquema.
