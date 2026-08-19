# Divisão de Tarefas — Trabalho Prático de Gerência de Configuração

Tema: **Docker Compose** · Modalidade: **Prática** (protótipo funcional + documentação técnica)
Disciplina: Gerência de Configuração — UFCA · Avaliação da 2ª unidade

Este documento organiza o trabalho que falta para atender aos requisitos do edital
(`Trabalho Prático - Gerência de Configuração-1.pdf`) e do resumo da equipe
(`resumo-trabalho-gerencia-configuracao-docker-compose.pdf`), a partir do que **já existe**
no repositório. Cada frente abaixo corresponde a uma pasta na raiz do projeto.

- - -

## 1. Estado atual do repositório (diagnóstico)

_Atualizado em 19/08/2026 após nova varredura do repositório._

| Item | Situação |
|---|---|
| `analise_critica_de_ecossistema/analise_critica.md` | ⚠️ Texto completo (ecossistema, pontos positivos, limitações, quando usar, conclusão), mas **ainda sem seção de referências bibliográficas** e o trecho sobre Kubernetes **ainda não foi reduzido/linkado** para `ComposeXKubernetes/` — as duas pendências da rodada anterior continuam abertas |
| `analise_critica_de_ecossistema/simulador_compose_python/` | ✅ Feito — simulador didático em Python (services, `depends_on`, rede, env vars, volume) |
| `exemplos_praticos/sistema_pedidos/` (infra: `db` + `redis` + `adminer`) | ✅ Feito e validado — `compose.yaml` com healthcheck, redes segregadas, volumes nomeados, profile `ferramentas` |
| `exemplos_praticos/sistema_pedidos/db/init/001_schema.sql` + `docs/banco-de-dados.md` | ✅ Feito |
| `exemplos_praticos/sistema_pedidos/docs/arquitetura.md` | ⚠️ Ainda descreve API, worker e frontend como **"componentes previstos"** — nenhuma mudança desde a última revisão |
| API + worker + frontend do sistema de pedidos | ❌ Não iniciado — `compose.yaml` só tem `db`, `redis`, `adminer`, `backend`/`ferramentas` e os dois volumes; é a peça que falta para fechar o exemplo complexo |
| Pasta **Contexto e fundamentos** (`contexto_e_fundamentos/fundamentos.md`) | ✅ Completo — histórico (Fig → Docker Inc. → Compose Specification), motivação, conceitos com trechos reais do `sistema_pedidos`, diagrama Mermaid e referências bibliográficas numeradas. Único problema: o link para "Compose vs. Kubernetes" aponta para `../compose_vs_kubernetes/`, pasta que **não existe** (ver achado abaixo) |
| Pasta **Compose vs. Containers** (`compose_vs_containers/compose_vs_containers.md`) | ⚠️ Documento escrito (comparação, tabela, vantagens/limitações, conclusão, referências), mas a **demonstração prática** exigida no edital não foi de fato realizada: o texto linka para uma pasta `./exemplo` que **não existe no repositório**, e não há prints/terminal output registrados |
| Pasta **Compose vs. Kubernetes** | ⚠️ Existe, mas com **nome divergente do planejado**: a pasta é `ComposeXKubernetes/kompose-exemplo/` (não `compose_vs_kubernetes/`). Contém uma demo prática funcional (compose → `kompose convert` → manifests → Minikube, com Makefile e script de verificação), porém **falta o documento comparativo** em si (tabela arquitetural, mapeamento conceitual `services→Deployment`, critérios de migração) descrito no item 4 da divisão — hoje só há um README de instruções de execução |
| `README.md` (raiz) | ⚠️ Sem mudanças — **Sumário** e **Como executar** continuam vazios; falta cabeçalho institucional (UFCA, disciplina, professor) e a lista de referências ainda tem só 2 links genéricos |
| Evidências (prints/vídeos) da demonstração | ❌ Não geradas ainda |
| Apresentação (slides ou roteiro) | ❌ Não iniciada |

**Principais mudanças desde a última rodada:** as frentes 1 (Contexto e fundamentos), 3
(Compose vs. Containers) e 4 (Compose vs. Kubernetes) saíram do zero e têm conteúdo — mas
nenhuma das três está 100% fechada. O que falta agora é mais cirúrgico: link quebrado em
`fundamentos.md`, demonstração prática ausente em `compose_vs_containers`, documento
comparativo ausente em `ComposeXKubernetes`, e as duas pendências antigas da análise crítica
(referências + corte do trecho sobre Kubernetes). O exemplo complexo (API/worker/frontend)
segue como o maior bloco de trabalho pendente.

- - -

## 2. Visão geral da divisão

| # | Frente | Responsável(is) | Pasta | Status |
|---|---|---|---|---|
| 1 | Contexto e fundamentos | Alan, Diogo | `contexto_e_fundamentos/` | ✅ Completo — só corrigir 1 link quebrado |
| 2 | Análise crítica e ecossistema | Neto | `analise_critica_de_ecossistema/` | ⚠️ Faltam referências + corte do trecho Kubernetes |
| 3 | Compose vs. Containers | Maria Antônia | `compose_vs_containers/` | ⚠️ Texto pronto — falta a demonstração prática |
| 4 | Compose vs. Kubernetes | CJ (Cicero Jesus) | `ComposeXKubernetes/kompose-exemplo/` | ⚠️ Demo prática pronta — falta o documento comparativo |
| 5 | Exemplos práticos | Todo o grupo (Matheus e Abner no exemplo complexo) | `exemplos_praticos/` | Infra pronta, aplicação (API/worker/frontend) pendente |

Tarefas que não pertencem a uma única pessoa (README raiz, referências, ensaio da
apresentação) estão na seção 4 — **Tarefas transversais**.

- - -

## 3. Detalhamento por frente

### 1. Contexto e fundamentos — Alan, Diogo

**Objetivo:** cobrir os itens "pesquisa bibliográfica" e "contextualização" exigidos no edital
(por que o Compose surgiu, que problema resolve) e os conceitos-base que todas as outras
frentes vão referenciar.

**Entregável:** `contexto_e_fundamentos/fundamentos.md`

Conteúdo esperado:
- Histórico: origem no projeto *Fig*, absorção pela Docker Inc., evolução do formato
  (`docker-compose.yml` v1/v2/v3 → *Compose Specification* → plugin `docker compose` v2
  integrado à CLI do Docker, substituindo o binário standalone `docker-compose`).
- Problema que motivou o Compose: orquestrar múltiplos containers sem depender de vários
  comandos `docker run` manuais (redes e volumes criados na mão, ordem de start manual).
- Conceitos e mecanismos, com trechos de exemplo **reaproveitando o `compose.yaml` real do
  `sistema_pedidos`** (já tem tudo isso implementado):
  - `services` (db, redis, adminer);
  - `networks` (rede `backend` interna vs. `ferramentas` com bridge);
  - `volumes` nomeados (`postgres_data`, `redis_data`);
  - variáveis de ambiente e interpolação (`${POSTGRES_DB:?...}`);
  - `depends_on` com `condition: service_healthy`;
  - `healthcheck` (`pg_isready`, `redis-cli ping`).
- Um diagrama simples (Mermaid ou imagem) mostrando a relação `services` → `networks` →
  `volumes`.

**Status: ✅ Conteúdo completo.** `fundamentos.md` já cobre histórico (Fig → aquisição pela
Docker Inc. → evolução v1/v2/v3 → Compose Specification → migração para o plugin `docker
compose` v2), o problema que motivou a ferramenta, os 6 mecanismos pedidos com trechos reais
do `sistema_pedidos`, diagrama Mermaid `services → networks → volumes` e referências
bibliográficas numeradas.

Pendência única:
- [ ] Corrigir o link em "5. Onde aprofundar cada conceito" — aponta para
  `../compose_vs_kubernetes/`, mas a pasta real (criada por CJ) é
  `ComposeXKubernetes/kompose-exemplo/`. Ajustar o link (e, idealmente, alinhar o nome da
  pasta ao padrão `snake_case` das demais — ver nota na seção 4).

**Dependências:** nenhuma. As outras frentes já linkam para este documento em vez de repetir
definições básicas.

- - -

### 2. Análise crítica e ecossistema — Neto

**Objetivo:** o conteúdo já existe e está bem escrito; falta fechar duas lacunas.

**Entregável:** ajustes em `analise_critica_de_ecossistema/analise_critica.md`

**Status: ⚠️ Ainda sem alterações** — as duas tarefas abaixo seguem exatamente como na
rodada anterior:

Tarefas:
- [ ] Adicionar **referências bibliográficas** citadas inline (confirmado: o arquivo hoje
  termina em "Conclusão crítica" sem nenhuma seção de fontes — o edital exige referências
  confiáveis e uma seção específica).
- [ ] A seção "Limitações e críticas" e a seção "Quando usar" ainda citam Kubernetes em
  detalhe. Agora que CJ já tem uma pasta com conteúdo (`ComposeXKubernetes/kompose-exemplo/`,
  ainda que só a demo prática), dá para **reduzir esse trecho a 1–2 frases e linkar para lá**
  — mas alinhar com CJ o nome final da pasta/arquivo antes, já que hoje diverge do padrão
  `compose_vs_kubernetes/` usado no restante do repositório.
- [ ] Opcional: um diagrama simples do ecossistema Docker (Engine, Dockerfile, Hub,
  Compose) para dar suporte visual na apresentação.

**Dependências:** o link para a frente 4 já pode ser fechado — a pasta existe — mas vale
confirmar com CJ se o nome/local do documento comparativo (ainda a ser escrito, ver seção 4)
vai mudar antes de linkar.

- - -

### 3. Compose vs. Containers — Maria Antônia

**Objetivo:** cobrir o item obrigatório "Comparação prática: Compose vs. containers
gerenciados manualmente — vantagens, limitações, cenários de uso", incluindo a demonstração
lado a lado sugerida no resumo do grupo.

**Entregável:** `compose_vs_containers/compose_vs_containers.md`

**Status: ⚠️ Texto pronto, demonstração prática pendente.** O documento já cobre:
- ✅ Tabela comparativa (nº de comandos, criação manual de rede, gestão de dependências,
  reprodutibilidade, versionamento, curva de aprendizado);
- ✅ Vantagens e limitações de cada abordagem, com cenários de uso recomendados;
- ✅ Referências bibliográficas.

O que falta:
- [ ] **Demonstração prática de fato**: a conclusão do documento (seção 6) menciona um
  exemplo em [`exemplo/`](./exemplo) com Flask + Redis rodando via `docker run` e depois via
  `docker compose`, mas **essa pasta não existe no repositório** — é um link quebrado hoje.
  Criar o exemplo (pode reaproveitar um recorte simples do `sistema_pedidos`, ex.: só `db` +
  `redis`, ou o Flask+Redis já mencionado no texto) e registrar os comandos usados em cada
  caminho lado a lado.
- [ ] Evidências: prints/terminal output de ambos os fluxos (para a apresentação e para o
  requisito de "evidências do funcionamento").

**Dependências:** pode reaproveitar o `compose.yaml` do `sistema_pedidos` (já estável). Não
bloqueia nem é bloqueado por outras frentes.

- - -

### 4. Compose vs. Kubernetes — CJ

**Objetivo:** cobrir o ponto de análise crítica destacado no resumo do grupo — Compose é
para orquestração local/desenvolvimento, não substitui um orquestrador de produção.

**Entregável esperado originalmente:** `compose_vs_kubernetes/compose-vs-kubernetes.md`
**O que existe hoje:** `ComposeXKubernetes/kompose-exemplo/` — nome e local diferentes do
planejado.

**Status: ⚠️ Só a parte prática está pronta.** CJ já implementou uma demo funcional e bem
documentada:
- ✅ `compose.yaml` minimalista (Nginx) convertido com `kompose convert` em
  `kubernetes-gerado/`, com manifests de referência anotados em `manifestos-referencia/`;
- ✅ `Makefile` com o fluxo completo (`verificar`, `compose`, `testar-compose`, `kubernetes`,
  `testar-kubernetes`, `escalar`, `limpar`) e `verificar-ambiente.sh`;
- ✅ README explicando o passo a passo Compose → Kompose → Minikube, incluindo o comando de
  escala (`kubectl scale --replicas=3`) que ilustra o que o Compose sozinho não oferece.

O que falta é o **documento comparativo em si**, previsto no edital e ainda não escrito:
- [ ] Diferenças arquiteturais: single-host (Compose) vs. cluster multi-node (Kubernetes).
- [ ] Tabela comparativa: auto-scaling, self-healing, service discovery, balanceamento de
  carga, service mesh, rollout/rollback, curva de aprendizado, complexidade operacional.
- [ ] Mapeamento conceitual (útil para quem já leu `contexto_e_fundamentos/`):
  `services` → Deployment + Service; `volumes` → PersistentVolume/PVC; `networks` →
  Namespace/Service; `environment` → ConfigMap/Secret; `depends_on` + `healthcheck` →
  readiness/liveness probes + initContainers.
- [ ] Critérios objetivos para decidir "quando migrar de Compose para Kubernetes" (carga,
  necessidade de múltiplos hosts, SLA, equipe de operação).
- [ ] Decidir e padronizar o nome/local final da pasta — hoje `ComposeXKubernetes` foge do
  padrão `snake_case` usado em `contexto_e_fundamentos/`, `compose_vs_containers/` e
  `analise_critica_de_ecossistema/`. Renomear (ou manter e só documentar a exceção) antes de
  outras frentes linkarem para cá — `fundamentos.md` já tem um link quebrado esperando por
  isso (ver seção 1).

**Dependências:** terminologia de `contexto_e_fundamentos/fundamentos.md` já está pronta para
reaproveitar. Avisar Neto quando o documento comparativo (e o nome definitivo da pasta)
estiverem prontos, para ele linkar de volta a partir de `analise_critica.md` e para Alan/Diogo
corrigirem o link em `fundamentos.md`.

- - -

### 5. Exemplos práticos — todo mundo, com Matheus e Abner no exemplo complexo

A base de dados do `sistema_pedidos` **já está pronta e validada**
(`compose.yaml`, `db/init/001_schema.sql`, healthchecks, redes segregadas). O que falta é
fechar o fluxo completo descrito em `docs/arquitetura.md`, que hoje é só "previsto":

```text
Navegador -> frontend -> API -> PostgreSQL
                             -> Redis -> worker -> PostgreSQL
```

**Matheus e Abner — exemplo complexo (`exemplos_praticos/sistema_pedidos/`)**

- [ ] `api/` — serviço simples (ex.: Node/Express, Python/FastAPI ou similar) com:
  - `POST /pedidos` (cria pedido, grava no Postgres, publica tarefa no Redis);
  - `GET /pedidos` e `GET /pedidos/:id`;
  - `Dockerfile` próprio.
- [ ] `worker/` — processo que consome a fila do Redis, atualiza o `status` do pedido no
  Postgres (`pendente` → `processando` → `processado`/`falhou`), com `Dockerfile`.
- [ ] `frontend/` — interface mínima (HTML/JS simples é suficiente) para criar e listar
  pedidos via API, com `Dockerfile`.
- [ ] Atualizar `compose.yaml`: adicionar os três serviços, com `depends_on` usando
  `condition: service_healthy` apontando para `db`/`redis` (API e worker) e para a API
  (frontend), seguindo o contrato já descrito em `docs/arquitetura.md`.
- [ ] Atualizar `docs/arquitetura.md` removendo o rótulo "previstos" e documentando o que
  foi de fato implementado.
- [ ] Estender `docs/validacao-infraestrutura.md` (ou criar `docs/validacao-fluxo-completo.md`)
  com o teste end-to-end: criar pedido pela API/frontend → conferir no Postgres → conferir
  mudança de status após o worker processar.
- [ ] Capturar evidências (prints ou vídeo curto) do fluxo completo rodando — necessário
  para a demonstração na apresentação.

**Todo o grupo — exemplos complementares mais simples**

Cada frente (1, 3, 4) já carrega ou deveria carregar um exemplo prático pequeno e focado no
próprio tema:
- ✅ Alan/Diogo: trecho de `compose.yaml` anotado ilustrando cada conceito (services,
  networks, volumes, depends_on, healthcheck) em `contexto_e_fundamentos/`.
- ✅ Neto: simulador Python já pronto em `simulador_compose_python/`.
- ⚠️ Maria Antônia: texto pronto, mas a demonstração `docker run` vs. `docker compose up`
  ainda não existe de fato (link para `./exemplo` quebrado — ver seção 3).
- ✅ CJ: foi além do "esboço não executável" sugerido — implementou uma demo real com
  `kompose convert` + Minikube em `ComposeXKubernetes/kompose-exemplo/`. Falta só o
  documento comparativo que interpreta essa demo (ver seção 4).

Isso satisfaz "exemplos práticos (todo mundo)" sem duplicar o esforço do exemplo complexo,
assim que o exemplo de Maria Antônia for criado.

- - -

## 4. Tarefas transversais (não são de uma pessoa só)

- [ ] **README raiz** (`README.md`): preencher o **Sumário** com links para as 5 pastas de
  conteúdo, escrever **Como executar** (passo a passo: clonar, `cp .env.example .env`,
  `docker compose up -d --wait`, onde olhar cada exemplo), acrescentar cabeçalho
  institucional (UFCA, curso, disciplina, nome do professor) e nomes completos da equipe —
  exigido explicitamente no checklist do edital. Sugestão: **Diogo** consolida isso depois
  que as pastas 1–4 tiverem pelo menos um rascunho, para linkar tudo corretamente.
- [ ] **Referências bibliográficas**: cada frente deve alimentar sua própria lista de fontes;
  o README raiz reúne a lista consolidada final (uma seção específica, como já existe hoje,
  mas hoje só tem 2 links genéricos).
- [ ] **Revisão cruzada**: depois que cada pasta tiver um primeiro rascunho, trocar de
  revisor (quem não escreveu o documento revisa). O resumo da equipe recomenda isso
  explicitamente.
- [ ] **Ensaio da apresentação completa**: todos os integrantes devem estar aptos a
  responder sobre qualquer parte do trabalho, não só a própria — a nota individual depende
  disso.
- [ ] **Cadência de commits**: o edital exige histórico distribuído ao longo do tempo, não
  um único commit final. O histórico atual já está bom (commits incrementais); manter esse
  padrão em todas as frentes.
- [ ] **Evidências de funcionamento**: prints/vídeos de cada exemplo prático (infra do
  sistema de pedidos, fluxo completo, comparação `docker run` vs. `compose`) — pedidos
  explicitamente no edital e necessários para quando a demo ao vivo não for viável.

- - -

## 5. Ordem sugerida de execução (atualizada em 19/08/2026)

Os marcos 1 e 2 da ordem original já foram cumpridos: `fundamentos.md` está completo e as
frentes 3/4 saíram do zero. O que resta é fechar as lacunas específicas, não mais abrir as
frentes:

1. **Pode ser feito imediatamente e em paralelo:**
   - Alan/Diogo: corrigir o link quebrado em `fundamentos.md` (seção 1);
   - Maria Antônia: criar o exemplo prático `compose_vs_containers/exemplo/` e capturar as
     evidências (seção 3);
   - CJ: escrever o documento comparativo (tabelas, mapeamento conceitual, critérios de
     migração) usando a demo já pronta como base (seção 4);
   - Matheus/Abner: seguir com API/worker/frontend do `sistema_pedidos` (seção 5) — maior
     bloco de trabalho pendente, não depende de nada acima.
2. **Ajustes na análise crítica (2)** — Neto já pode reduzir o trecho sobre Kubernetes e
   linkar para `ComposeXKubernetes/kompose-exemplo/`, mas convém alinhar antes com CJ se o
   nome/local da pasta vai mudar (para não linkar um caminho que será renomeado). A adição
   das referências bibliográficas não tem essa dependência e pode ser feita já.
3. **README raiz e referências consolidadas** — quando os itens acima estiverem fechados
   (ou pelo menos sem links quebrados) e o exemplo complexo (5) estiver funcional.
4. **Evidências, revisão cruzada e ensaio da apresentação** — na reta final, com o
   repositório já estruturado.

Prazo exato e duração da apresentação ainda não foram confirmados com o professor
(conforme observação no resumo da equipe) — confirmar antes de fechar o cronograma.
