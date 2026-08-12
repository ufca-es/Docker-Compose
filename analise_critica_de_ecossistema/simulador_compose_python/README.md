# Simulador de Docker Compose em Python

Este exemplo nao usa Docker. Ele apenas simula alguns conceitos do Docker Compose para facilitar a apresentacao:

- servicos;
- dependencia entre servicos;
- rede interna;
- variaveis de ambiente;
- volume para persistencia de dados.

## Como executar

Dentro desta pasta, rode:

```bash
python simulador_compose.py
```

O script cria uma pasta chamada `volume_dados` e salva um banco SQLite nela. Ao executar novamente, o contador aumenta, simulando a persistencia de dados de um volume.

## Relacao com Docker Compose

No Docker Compose real, os servicos seriam containers. Neste simulador:

- `app` representa uma aplicacao Python;
- `db` representa um banco de dados;
- `volume_dados` representa um volume Docker;
- `DB_HOST=db` representa a comunicacao pela rede interna do Compose.
