# Docker Compose vs. Containers

## 1. Introdução

Ao trabalhar com Docker, é comum começar gerenciando **containers individuais** através do comando `docker run`. Esse fluxo funciona bem quando a aplicação é simples e roda em um único container. Porém, a maioria das aplicações reais é composta por **múltiplos serviços** que precisam se comunicar entre si - por exemplo, uma API, um banco de dados e um cache.

É nesse cenário que entra o **Docker Compose**: uma ferramenta que permite definir e gerenciar aplicações multi-container de forma declarativa, usando um único arquivo de configuração (`docker-compose.yml`).

Este documento explica as diferenças entre gerenciar containers manualmente e usar o Docker Compose, destacando vantagens, desvantagens e quando usar cada abordagem.

---

## 2. Containers "puros" (gerenciados manualmente)

Um **container** é uma instância em execução de uma imagem Docker. Ele é criado, iniciado, parado e removido através de comandos individuais como:

```bash
docker build -t meu-app .
docker network create minha-rede
docker run -d --name redis --network minha-rede redis:7
docker run -d --name app --network minha-rede -p 5000:5000 meu-app
```

### Características

- Cada container é criado e configurado **separadamente**, via linha de comando.
- A comunicação entre containers exige criação manual de redes (`docker network`) e o uso correto de nomes/hostnames.
- Não existe um "estado" declarado da aplicação: se você esquecer um parâmetro (uma variável de ambiente, uma porta, um volume), a aplicação simplesmente não vai funcionar como esperado.
- Escalar, atualizar ou recriar o ambiente exige repetir manualmente todos os comandos, na ordem certa.
- É fácil cometer erros de digitação ou esquecer flags, principalmente em ambientes com muitos serviços.

### Quando faz sentido usar apenas containers

- Testes rápidos e isolados de uma única imagem.
- Depuração pontual de um serviço específico.
- Ambientes muito simples, com um único container e sem dependências externas.

---

## 3. Docker Compose

O **Docker Compose** é uma ferramenta que permite descrever, em um arquivo YAML (`docker-compose.yml`), todos os serviços, redes e volumes que compõem uma aplicação. Com um único comando, é possível subir (ou derrubar) toda a infraestrutura:

```bash
docker compose up -d
docker compose down
```

### Características

- **Declarativo**: toda a configuração (imagens, portas, variáveis de ambiente, volumes, redes, dependências entre serviços) fica descrita em um único arquivo, versionável junto com o código.
- **Rede automática**: o Compose cria automaticamente uma rede interna, permitindo que os serviços se comuniquem entre si usando o **nome do serviço** como hostname (ex: um serviço `app` pode acessar o banco simplesmente usando o host `db`).
- **Orquestração de dependências**: é possível definir a ordem de inicialização dos serviços com `depends_on`.
- **Reprodutibilidade**: qualquer pessoa que clone o repositório e rode `docker compose up` terá exatamente o mesmo ambiente, sem precisar decorar comandos.
- **Ciclo de vida simplificado**: subir, parar, reconstruir e remover toda a stack com comandos únicos (`up`, `down`, `build`, `logs`, `ps`).

### Quando faz sentido usar Docker Compose

- Aplicações com múltiplos serviços (API + banco de dados + cache + fila, etc.).
- Ambientes de desenvolvimento local que precisam ser fáceis de reproduzir.
- Times que precisam compartilhar uma configuração de ambiente padronizada.
- Testes de integração entre serviços.

---

## 4. Comparação direta

A tabela abaixo compara os dois fluxos considerando o cenário do nosso exemplo prático: subir **dois serviços** (aplicação + Redis) que precisam se comunicar entre si.

| Critério                                    | Containers (`docker run`)                                          | Docker Compose (`docker compose up`)             |
|-----------------------------------------------|------------------------------------------------------------------------|------------------------------------------------------|
| **Nº de comandos para subir o ambiente**       | 4 comandos (criar rede, subir Redis, buildar imagem, subir app)          | 1 comando (`docker compose up -d --build`)             |
| **Criação de rede**                           | Manual, via `docker network create`, antes de subir os containers        | Automática - o Compose cria a rede ao rodar `up`        |
| **Gestão de dependências entre containers**    | Manual: o desenvolvedor precisa saber e respeitar a ordem certa           | Declarativa, via `depends_on` no YAML                   |
| **Reprodutibilidade**                          | Baixa - depende de lembrar/documentar todos os comandos e flags           | Alta - o mesmo `docker-compose.yml` recria o ambiente idêntico em qualquer máquina |
| **Versionamento do ambiente**                  | Difícil - comandos soltos, normalmente ficam em anotações ou scripts avulsos | Fácil - o `docker-compose.yml` é um arquivo de texto, versionado no Git junto com o código |
| **Curva de aprendizado**                       | Baixa para um único container; cresce rápido com múltiplos serviços       | Um pouco maior no início (sintaxe do YAML), mas se paga rapidamente com 2+ serviços |

---

## 4.1. Vantagens e limitações

### Containers gerenciados manualmente

**Vantagens**
- Simplicidade para um único container isolado, sem necessidade de arquivo de configuração extra.
- Controle fino e imediato: cada flag é decidida no momento da execução do comando.
- Bom para testes rápidos e descartáveis de uma imagem específica.

**Limitações**
- Não escala bem: quanto mais serviços, mais comandos, mais chance de erro humano (esquecer uma flag, uma porta, o nome da rede).
- Nenhum registro formal do ambiente - se o desenvolvedor não documentar os comandos em algum lugar, o conhecimento se perde.
- Dificulta o trabalho em equipe, pois cada pessoa pode montar o ambiente de um jeito ligeiramente diferente.

**Cenários recomendados**: depuração pontual de uma imagem, testes isolados, provas de conceito rápidas com um único serviço.

### Docker Compose

**Vantagens**
- Um único arquivo declarativo descreve toda a stack (serviços, redes, volumes, variáveis de ambiente).
- Ambiente reprodutível: qualquer pessoa do time sobe a mesma stack com o mesmo comando.
- Versionável junto com o código-fonte, o que facilita histórico de mudanças e revisão em Pull Requests.
- Gerencia automaticamente rede e ordem de dependência entre serviços.

**Limitações**
- Exige aprender a sintaxe do `docker-compose.yml` (ainda que simples).
- Para orquestração em produção e em larga escala, geralmente é substituído por ferramentas mais robustas, como Kubernetes ou Docker Swarm - o Compose é focado principalmente em desenvolvimento local e ambientes menores.
- Um único arquivo mal escrito pode impactar todos os serviços da stack ao mesmo tempo.

**Cenários recomendados**: desenvolvimento local de aplicações multi-serviço, ambientes de teste/integração, times que precisam padronizar a configuração do ambiente entre todos os desenvolvedores.

---

## 5. Conclusão

O Docker Compose não substitui os containers - ele é construído **em cima** deles. Cada serviço definido no `docker-compose.yml` ainda se torna, por trás dos panos, um container Docker comum. A diferença está na **camada de orquestração**: o Compose organiza, conecta e gerencia o ciclo de vida de múltiplos containers de forma simples e reprodutível.

Em resumo:

- Use **containers individuais** para tarefas simples, pontuais ou isoladas.
- Use **Docker Compose** sempre que a aplicação envolver múltiplos serviços que precisam trabalhar juntos.

Um exemplo prático dessa diferença está disponível na pasta [`exemplo/`](./exemplo), onde uma aplicação Flask + Redis é executada primeiro manualmente (com `docker run`) e depois com Docker Compose, evidenciando a diferença de complexidade entre as duas abordagens.

---

## 6. Referências

- [Documentação oficial do Docker Compose](https://docs.docker.com/compose/)
- [Docker Curriculum](https://docker-curriculum.com/)
- [Rede de containers no Docker](https://docs.docker.com/network/)
- [Docker e Docker Compose um guia para iniciantes.](https://dev.to/ingresse/docker-e-docker-compose-um-guia-para-iniciantes-48k8)
