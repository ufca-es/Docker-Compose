# Divisão de Tarefas — Trabalho Prático de Gerência de Configuração

Tema: **Docker Compose** · Modalidade: **Prática** (protótipo funcional + documentação técnica)
Disciplina: Gerência de Configuração — UFCA · Avaliação da 2ª unidade

Este documento organiza o trabalho que falta para atender aos requisitos do edital
(`Trabalho Prático - Gerência de Configuração-1.pdf`) e do resumo da equipe
(`resumo-trabalho-gerencia-configuracao-docker-compose.pdf`), a partir do que **já existe**
no repositório. Cada frente abaixo corresponde a uma pasta na raiz do projeto.

- - -

## 1. Estado atual do repositório (diagnóstico)

| Item | Situação |
|---|---|
| `analise_critica_de_ecossistema/analise_critica.md` | ✅ Feito — análise crítica completa (ecossistema, pontos positivos, limitações, quando usar, conclusão) |
| `analise_critica_de_ecossistema/simulador_compose_python/` | ✅ Feito — simulador didático em Python (services, `depends_on`, rede, env vars, volume) |
| `exemplos_praticos/sistema_pedidos/` (infra: `db` + `redis` + `adminer`) | ✅ Feito e **validado** (17/08/2026) — `compose.yaml` com healthcheck, redes segregadas, volumes nomeados, profile `ferramentas` |
| `exemplos_praticos/sistema_pedidos/db/init/001_schema.sql` + `docs/banco-de-dados.md` | ✅ Feito |
| `exemplos_praticos/sistema_pedidos/docs/arquitetura.md` | ⚠️ Descreve API, worker e frontend como **"componentes previstos"** — ainda não implementados |
| API + worker + frontend do sistema de pedidos | ❌ Não iniciado — é a peça que falta para fechar o exemplo complexo |
| Pasta de **Contexto e fundamentos** | ✅ Rascunho pronto (`fundamentos.md`) — falta revisão do Alan |
| Pasta de **Compose vs. Containers** | ❌ Não existe |
| Pasta de **Compose vs. Kubernetes** | ❌ Não existe |
| `README.md` (raiz) | ⚠️ Tem tabela da equipe, mas **Sumário** e **Como executar** estão vazios; falta cabeçalho institucional (UFCA, disciplina, professor) e referências específicas por tema |
| Evidências (prints/vídeos) da demonstração | ❌ Não geradas ainda |
| Apresentação (slides ou roteiro) | ❌ Não iniciada |

Ou seja: a fundação técnica (infra de dados do Compose) e a análise crítica estão em bom
estado. O que falta é justamente distribuído entre as frentes 1, 3, 4 e a parte funcional da 5.

- - -

## 2. Visão geral da divisão

| # | Frente | Responsável(is) | Pasta | Status |
|---|---|---|---|---|
| 1 | Contexto e fundamentos | Alan, Diogo | `contexto_e_fundamentos/` | Rascunho pronto — falta revisão do Alan |
| 2 | Análise crítica e ecossistema | Neto | `analise_critica_de_ecossistema/` | Revisão/ajuste fino |
| 3 | Compose vs. Containers | Maria Antônia | `compose_vs_containers/` | A criar |
| 4 | Compose vs. Kubernetes | CJ (Cicero Jesus) | `compose_vs_kubernetes/` | A criar |
| 5 | Exemplos práticos | Todo o grupo (Matheus e Abner no exemplo complexo) | `exemplos_praticos/` | Infra pronta, aplicação pendente |

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

**Dependências:** nenhuma — pode começar imediatamente. As outras frentes vão linkar para
este documento em vez de repetir definições básicas.

- - -

### 2. Análise crítica e ecossistema — Neto

**Objetivo:** o conteúdo já existe e está bem escrito; falta fechar duas lacunas.

**Entregável:** ajustes em `analise_critica_de_ecossistema/analise_critica.md`

Tarefas:
- [ ] Adicionar **referências bibliográficas** citadas inline (o texto faz afirmações sobre
  maturidade/ecossistema sem link de apoio — o edital exige referências confiáveis e uma
  seção específica).
- [ ] A seção "Limitações e críticas" já cita Kubernetes como contraponto. Como a frente 4
  (CJ) vai aprofundar exatamente essa comparação, **reduzir esse trecho a 1–2 frases e
  linkar para `compose_vs_kubernetes/`** para evitar conteúdo duplicado entre os dois temas.
- [ ] Opcional: um diagrama simples do ecossistema Docker (Engine, Dockerfile, Hub,
  Compose) para dar suporte visual na apresentação.

**Dependências:** o link para a frente 4 só pode ser fechado depois que CJ criar o
documento (ou pelo menos definir o nome do arquivo).

- - -

### 3. Compose vs. Containers — Maria Antônia

**Objetivo:** cobrir o item obrigatório "Comparação prática: Compose vs. containers
gerenciados manualmente — vantagens, limitações, cenários de uso", incluindo a demonstração
lado a lado sugerida no resumo do grupo.

**Entregável:** `compose_vs_containers/compose-vs-containers.md`

Conteúdo esperado:
- Tabela comparativa: nº de comandos, criação manual de rede, gestão de dependências entre
  containers, reprodutibilidade, versionamento do ambiente, curva de aprendizado.
- Vantagens e limitações de cada abordagem, com cenários de uso recomendados para cada uma.
- **Demonstração prática**: subir os mesmos serviços via `docker run` manual (múltiplos
  comandos, rede criada na mão) vs. `docker compose up` (um único comando). Pode reaproveitar
  um recorte simples do `sistema_pedidos` (ex.: só `db` + `redis`) ou um exemplo próprio
  minimalista — o importante é registrar os comandos usados em cada caminho lado a lado.
- Evidências: prints/terminal output de ambos os fluxos (para a apresentação e para o
  requisito de "evidências do funcionamento").

**Dependências:** pode reaproveitar o `compose.yaml` do `sistema_pedidos` assim que a base
estiver estável (já está). Não bloqueia nem é bloqueado por outras frentes.

- - -

### 4. Compose vs. Kubernetes — CJ

**Objetivo:** cobrir o ponto de análise crítica destacado no resumo do grupo — Compose é
para orquestração local/desenvolvimento, não substitui um orquestrador de produção.

**Entregável:** `compose_vs_kubernetes/compose-vs-kubernetes.md`

Conteúdo esperado:
- Diferenças arquiteturais: single-host (Compose) vs. cluster multi-node (Kubernetes).
- Tabela comparativa: auto-scaling, self-healing, service discovery, balanceamento de carga,
  service mesh, rollout/rollback, curva de aprendizado, complexidade operacional.
- Mapeamento conceitual (útil para quem já leu `contexto_e_fundamentos/`):
  `services` → Deployment + Service; `volumes` → PersistentVolume/PVC; `networks` →
  Namespace/Service; `environment` → ConfigMap/Secret; `depends_on` + `healthcheck` →
  readiness/liveness probes + initContainers.
- Critérios objetivos para decidir "quando migrar de Compose para Kubernetes" (carga,
  necessidade de múltiplos hosts, SLA, equipe de operação).

**Dependências:** ler `contexto_e_fundamentos/fundamentos.md` primeiro (para reaproveitar a
terminologia) e avisar Neto quando o documento estiver pronto, para ele linkar de volta a
partir de `analise_critica.md`.

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

Cada frente (1, 3, 4) já carrega um exemplo prático pequeno e focado no próprio tema:
- Alan/Diogo: trecho de `compose.yaml` anotado ilustrando cada conceito (services,
  networks, volumes, depends_on, healthcheck) em `contexto_e_fundamentos/`.
- Neto: simulador Python já pronto em `simulador_compose_python/`.
- Maria Antônia: demonstração `docker run` vs. `docker compose up` em `compose_vs_containers/`.
- CJ: pode incluir um esboço de manifesto Kubernetes equivalente ao `compose.yaml` (sem
  precisar ser executável) só para ilustrar a comparação — o edital permite "trechos de
  código não executáveis" quando aplicável.

Isso satisfaz "exemplos práticos (todo mundo)" sem duplicar o esforço do exemplo complexo.

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

## 5. Ordem sugerida de execução

1. **Já pode rodar em paralelo agora:** Contexto e fundamentos (1), Compose vs. Containers (3),
   e o desenvolvimento de API/worker/frontend (5 — Matheus/Abner), pois nenhuma depende de
   outra pronta.
2. **Compose vs. Kubernetes (4)** deve começar depois de uma primeira versão do documento 1
   (fundamentos), para reaproveitar a terminologia.
3. **Ajustes na análise crítica (2)** — o corte do trecho sobre Kubernetes só deve ser feito
   depois que o documento 4 existir (mesmo que em rascunho), para linkar corretamente.
4. **README raiz e referências consolidadas** — por último, quando as pastas 1–4 tiverem
   pelo menos um rascunho e o exemplo complexo (5) estiver funcional.
5. **Evidências, revisão cruzada e ensaio da apresentação** — na reta final, com o
   repositório já estruturado.

Prazo exato e duração da apresentação ainda não foram confirmados com o professor
(conforme observação no resumo da equipe) — confirmar antes de fechar o cronograma.
