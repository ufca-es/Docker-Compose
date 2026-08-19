# Docker-Compose
pesquisa aplicada sobre Docker Compose + protótipo funcional que demonstre os conceitos na prática

- - -

## Sumário

- [Exemplo prático complexo: sistema de pedidos](exemplos_praticos/sistema_pedidos/README.md)
  - [Arquitetura](exemplos_praticos/sistema_pedidos/docs/arquitetura.md)
  - [Banco de dados](exemplos_praticos/sistema_pedidos/docs/banco-de-dados.md)
  - [Validação da infraestrutura](exemplos_praticos/sistema_pedidos/docs/validacao-infraestrutura.md)
  - [Validação do fluxo completo](exemplos_praticos/sistema_pedidos/docs/validacao-fluxo-completo.md)

- - -

## Equipe
| Nome | Usuário |
|---|---|
| Abner Levi | abnerlevi |
| Alan Mendes Vieira | alan-mendes-ufca |
| Cicero Jesus | cicero-jesus |
| Diogo Gomes | fgrdiogo |
| Maria Antônia | mariastrajano |
| Matheus Nogueira | mathsNS |
| Antônio Neto | netoo-444 |

- - - 

## Como executar

### Sistema de pedidos

O exemplo integra API FastAPI, worker, PostgreSQL, Redis e Adminer com redes, volumes, variáveis de ambiente, healthchecks e processamento assíncrono.

```bash
cd exemplos_praticos/sistema_pedidos
cp .env.example .env
docker compose --profile ferramentas up -d --build --wait
docker compose ps
```

No PowerShell, substitua o comando de cópia por:

```powershell
Copy-Item .env.example .env
```

Depois da inicialização:

- documentação interativa da API: `http://127.0.0.1:8000/docs`;
- Adminer: `http://127.0.0.1:8081`;
- instruções e demonstração: [exemplos_praticos/sistema_pedidos/README.md](exemplos_praticos/sistema_pedidos/README.md).

- - - 

## Referências bibliográficas

- [Ultimate Docker Compose Tutorial](https://www.youtube.com/watch?v=SXwC9fSwct8)
- [dockerdocs: Docker Compose](https://docs.docker.com/compose/)
