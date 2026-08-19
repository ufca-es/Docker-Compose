# Docker Compose x Kubernetes e o papel do Kompose

## 1. Introdução

Aplicações modernas frequentemente são distribuídas em contêineres. Um sistema
pode ter, por exemplo, um contêiner para a aplicação web, outro para o banco de
dados e outro para cache. Quando surgem vários contêineres, também surge a
necessidade de descrever como eles serão iniciados, conectados, configurados e
encerrados.

Docker Compose e Kubernetes ajudam a resolver esse problema, mas atuam em
escalas diferentes. O Compose prioriza a simplicidade para definir e executar
uma aplicação com vários contêineres, normalmente em um único Docker Engine. O
Kubernetes é uma plataforma de orquestração que administra aplicações em um
cluster, mantendo o estado desejado mesmo diante de falhas ou atualizações.

O Kompose aparece entre esses dois contextos: ele lê um arquivo Compose e gera
manifestos que servem como ponto de partida para executar a aplicação em
Kubernetes.

> **Ideia principal:** Docker Compose e Kubernetes não são apenas duas sintaxes
> diferentes para a mesma coisa. Eles possuem objetivos, arquitetura e custos
> operacionais diferentes.

---

## 2. Conceito necessário: contêiner não é máquina virtual

Um contêiner empacota uma aplicação com as bibliotecas e configurações de que
ela precisa. Diferentemente de uma máquina virtual completa, os contêineres
compartilham o kernel do sistema hospedeiro. Isso costuma tornar sua criação e
inicialização mais rápidas e econômicas.

Uma imagem é o modelo imutável usado para criar contêineres. O contêiner é uma
instância em execução dessa imagem. Docker Compose e Kubernetes não substituem
as imagens: ambos usam imagens de contêiner como parte da descrição da
aplicação.

---

## 3. O que é Docker Compose?

Docker Compose é uma ferramenta para definir e executar aplicações com vários
contêineres. A configuração é declarada em um arquivo YAML, normalmente chamado
`compose.yaml`. Nesse arquivo são descritos elementos como:

- **services:** os componentes da aplicação;
- **networks:** as redes usadas na comunicação entre serviços;
- **volumes:** os dados que precisam persistir;
- **configs e secrets:** configurações e dados sensíveis, quando utilizados.

Um exemplo mínimo é:

```yaml
services:
  web:
    image: nginx:1.27-alpine
    ports:
      - "8080:80"
```

O serviço chamado `web` usa a imagem Nginx. A porta 8080 da máquina é ligada à
porta 80 do contêiner. Toda a aplicação pode ser iniciada com:

```bash
docker compose up -d
```

O Compose interpreta o YAML, pede ao Docker Engine que crie os recursos e
organiza o ciclo de vida dos contêineres. Comandos comuns são:

```bash
docker compose ps
docker compose logs
docker compose stop
docker compose down
```

### Pontos fortes do Docker Compose

- curva de aprendizado pequena;
- um único arquivo descreve toda a aplicação;
- ótimo para desenvolvimento local, testes e demonstrações;
- reproduz o mesmo ambiente para diferentes integrantes da equipe;
- inicialização e remoção simples com `up` e `down`;
- integração direta com Dockerfiles e imagens locais.

### Limites importantes

O Compose controla os recursos de um Docker Engine por vez. Ele não possui um
control plane de cluster responsável por distribuir Pods entre diferentes nós,
reagendar cargas após a perda de um nó ou executar reconciliação distribuída.
É possível usá-lo em produção, especialmente em sistemas pequenos e
centralizados, mas alta disponibilidade e operação em vários servidores exigem
soluções adicionais.

---

## 4. O que é Kubernetes?

Kubernetes é uma plataforma aberta e extensível para administrar cargas de
trabalho e serviços em contêineres por meio de configuração declarativa e
automação. Em vez de descrever apenas quais contêineres devem ser iniciados, o
usuário declara um **estado desejado** para o cluster.

Por exemplo, pode-se declarar que devem existir três réplicas de uma aplicação.
Os controladores do Kubernetes observam continuamente o estado atual. Se um Pod
falhar e restarem apenas duas réplicas, o sistema tenta criar outra para voltar
ao estado desejado.

### Arquitetura resumida

Um cluster Kubernetes possui duas grandes partes:

```text
                     CLUSTER KUBERNETES

  +-------------------+       +---------------------------+
  |   Control plane   |       |       Worker nodes        |
  | API, scheduler e  | ----> | kubelet, runtime e Pods   |
  | controladores     |       | que executam a aplicação  |
  +-------------------+       +---------------------------+
```

O **control plane** recebe os manifestos, armazena o estado desejado, toma
decisões de agendamento e executa os controladores. Os **worker nodes** são as
máquinas que executam os Pods. O `kubectl` é um cliente que conversa com a API
do cluster; ele não é o cluster em si.

### Objetos principais

| Objeto | Função simplificada |
|---|---|
| **Pod** | Menor unidade implantável; contém um ou mais contêineres. |
| **Deployment** | Administra réplicas de Pods e atualizações de aplicações sem estado. |
| **Service** | Oferece endereço estável para acessar um conjunto variável de Pods. |
| **ConfigMap** | Armazena configuração não sensível. |
| **Secret** | Armazena dados sensíveis; ainda exige práticas adequadas de proteção. |
| **PersistentVolumeClaim** | Solicita armazenamento persistente para a aplicação. |
| **Ingress** | Define regras de entrada HTTP/HTTPS, dependendo de um controlador. |

Um manifesto simplificado de Deployment possui esta forma:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: web
          image: nginx:1.27-alpine
```

Depois de salvar o manifesto, ele pode ser enviado ao cluster:

```bash
kubectl apply -f web-deployment.yaml
```

O uso de `apply` demonstra a natureza declarativa: o arquivo informa o estado
pretendido, e o Kubernetes trabalha para alcançá-lo e mantê-lo.

### Pontos fortes do Kubernetes

- distribuição de cargas entre múltiplos nós;
- recuperação automática de Pods;
- escalabilidade horizontal;
- descoberta de serviços e balanceamento;
- atualizações graduais e possibilidade de rollback;
- configuração declarativa e extensível;
- ecossistema amplo para observabilidade, segurança e automação.

### Custos e dificuldades

- mais conceitos e arquivos para aprender;
- instalação e administração do cluster;
- maior consumo de recursos;
- rede, armazenamento e segurança são mais elaborados;
- observabilidade e diagnóstico exigem conhecimento operacional;
- para uma aplicação pequena em uma única máquina, pode ser complexidade
  desnecessária.

---

## 5. Comparação direta

| Critério | Docker Compose | Kubernetes |
|---|---|---|
| Objetivo central | Executar uma aplicação com vários contêineres de forma simples. | Orquestrar cargas de trabalho em um cluster. |
| Unidade descrita | Serviço do Compose. | Objetos como Pod, Deployment e Service. |
| Infraestrutura típica | Um Docker Engine. | Control plane e um ou mais worker nodes. |
| Arquivo | Geralmente um `compose.yaml`. | Um ou vários manifestos YAML e outros mecanismos de empacotamento. |
| Estado desejado | Recria e gerencia serviços por comandos do Compose. | Controladores reconciliam continuamente estado atual e desejado. |
| Recuperação de falhas | Políticas de reinício do contêiner no host. | Recriação e reagendamento de Pods conforme controladores e saúde do cluster. |
| Escala | Simples, principalmente em um host. | Réplicas, escalabilidade manual e automática no cluster. |
| Rede | Rede Docker e DNS pelos nomes dos serviços. | Rede de Pods, Services, DNS do cluster, Ingress e políticas. |
| Atualizações | Normalmente recriação dos contêineres. | Estratégias de rollout e histórico para rollback. |
| Alta disponibilidade | Não é sua finalidade principal. | É um objetivo possível quando cluster e aplicação são projetados para isso. |
| Curva de aprendizado | Menor. | Maior. |
| Uso mais comum | Desenvolvimento, testes, CI e aplicações menores. | Produção distribuída, escala e operação de muitos serviços. |

### Não confundir

- Docker é uma plataforma/ecossistema de contêineres; Kubernetes é um
  orquestrador e pode usar runtimes compatíveis com sua interface, como
  containerd ou CRI-O.
- Kubernetes não exige Docker Engine nos nós.
- `docker compose up` e `kubectl apply` podem parecer equivalentes em uma
  demonstração simples, mas ativam arquiteturas diferentes.
- Usar Kubernetes não torna uma aplicação automaticamente escalável ou
  altamente disponível. A aplicação e a infraestrutura precisam ser
  projetadas para isso.

---

## 6. Quando usar cada um?

### Use Docker Compose quando

- o objetivo é desenvolver localmente;
- a equipe precisa iniciar rapidamente aplicação, banco e cache;
- o trabalho é uma prova de conceito ou uma demonstração;
- a aplicação será executada em uma única máquina e interrupções breves são
  aceitáveis;
- simplicidade tem mais valor que recursos avançados de orquestração;
- é necessário reproduzir um ambiente de integração em CI.

### Use Kubernetes quando

- a aplicação precisa ser distribuída por vários servidores;
- há necessidade real de alta disponibilidade;
- existem muitos serviços e equipes compartilhando infraestrutura;
- são necessários rollouts, rollback, autoscaling ou políticas avançadas;
- o ambiente precisa reagir automaticamente a falhas;
- a organização possui capacidade para administrar o cluster ou utiliza um
  serviço Kubernetes gerenciado.

### Podem ser usados juntos?

Sim. É comum utilizar Compose no computador do desenvolvedor e Kubernetes em
homologação ou produção:

```text
desenvolvimento local        entrega/produção
     Compose        --->        Kubernetes
```

Entretanto, manter duas descrições pode causar divergências. Testes,
documentação, automação de CI/CD e revisão dos manifestos ajudam a reduzir esse
risco.

---

## 7. O que é Kompose?

Kompose é uma ferramenta de conversão que recebe uma configuração Compose e
gera objetos para Kubernetes ou OpenShift. O fluxo básico é:

```text
compose.yaml
     |
     | kompose convert
     v
Deployment(s), Service(s) e outros manifestos YAML
     |
     | kubectl apply -f ...
     v
cluster Kubernetes
```

O comando principal é:

```bash
kompose --file compose.yaml convert
```

Sem a opção `--provider`, Kubernetes é o destino padrão. O Kompose não executa
o Kubernetes nem cria sozinho um cluster: ele realiza a tradução. Para aplicar
o resultado, ainda são necessários um cluster e o `kubectl` configurado.

### Traduções comuns

| Compose | Resultado típico no Kubernetes |
|---|---|
| `services` | Deployment ou outro controlador para cada serviço. |
| `image` | Imagem do contêiner dentro do Pod. |
| `ports` | Portas do contêiner e, quando aplicável, um Service. |
| `environment` | Variáveis de ambiente do contêiner. |
| `volumes` | Volumes e possivelmente PersistentVolumeClaims. |
| nomes de serviços | Nomes e labels dos recursos Kubernetes. |
| labels `kompose.*` | Instruções adicionais para a conversão. |

Por exemplo, esta label pede a geração de um Service do tipo NodePort:

```yaml
labels:
  kompose.service.type: nodeport
```

### O que o Kompose não faz automaticamente

Kompose acelera uma migração inicial, mas o resultado precisa ser revisado. Nem
todo conceito do Compose possui equivalente exato em Kubernetes. Em um projeto
real, normalmente ainda é necessário avaliar:

- limites e solicitações de CPU e memória;
- liveness, readiness e startup probes;
- Secrets e ConfigMaps;
- classe e política de armazenamento;
- Ingress, TLS e DNS;
- permissões, ServiceAccounts e políticas de segurança;
- afinidade, tolerations e distribuição de réplicas;
- estratégia de atualização;
- observabilidade e políticas de rede.

O comando gera arquivos estáticos em um determinado momento. Se o
`compose.yaml` mudar depois, os manifestos não são sincronizados
automaticamente: será preciso converter novamente ou atualizar manualmente a
configuração Kubernetes. Avisos de opções ignoradas durante a conversão não
devem ser descartados.

> **Conclusão sobre o Kompose:** ele é uma ponte e um ponto de partida, não um
> substituto para aprender e revisar Kubernetes.

---

## 8. Exemplo prático deste trabalho

O exemplo está na pasta `kompose-exemplo`. Seu arquivo `compose.yaml` contém um
servidor Nginx:

```yaml
services:
  web:
    image: nginx:1.27-alpine
    ports:
      - "8080:80"
    labels:
      kompose.service.type: nodeport
      kompose.service.nodeport.port: "30080"
```

### Executar com Compose

```bash
cd kompose-exemplo
docker compose up -d
docker compose ps
curl http://localhost:8080
docker compose down
```

### Converter com Kompose

```bash
cd kompose-exemplo
mkdir -p kubernetes-gerado
cd kubernetes-gerado
kompose -f ../compose.yaml convert
ls -1
```

O resultado esperado é a criação de um Deployment e um Service. Nomes, labels,
anotações e formatação podem variar conforme a versão do Kompose.

### Aplicar em um cluster local

Com Minikube em execução:

```bash
minikube start
kubectl apply -f .
kubectl get deployments,pods,services
minikube service web --url
```

Para demonstrar uma capacidade do Kubernetes, aumente as réplicas:

```bash
kubectl scale deployment web --replicas=3
kubectl get pods
```

Para limpar os recursos:

```bash
kubectl delete -f .
minikube stop
```

---

## 9. Síntese final

Docker Compose resolve com simplicidade o problema de descrever e executar uma
aplicação composta por vários contêineres. Kubernetes resolve um problema mais
amplo: manter cargas de trabalho no estado desejado dentro de um cluster,
oferecendo mecanismos para distribuição, recuperação, escala e atualização.

A escolha não deve ser baseada apenas em qual ferramenta possui mais recursos.
Deve-se escolher a solução mais simples que atenda aos requisitos. Para
desenvolvimento local e aplicações pequenas, Compose costuma ser suficiente.
Para operação distribuída, escala e disponibilidade, Kubernetes pode ser mais
adequado, desde que seu custo operacional seja justificado.

Kompose ajuda a visualizar a passagem entre esses dois modelos. Ao converter
um serviço Compose em Deployment e Service, ele demonstra que a migração não é
somente uma troca de comandos: ela transforma uma descrição voltada ao Docker
Engine em objetos administrados continuamente por um cluster Kubernetes.

---

## Referências oficiais

- Docker. [Docker Compose](https://docs.docker.com/compose/).
- Docker. [Como o Compose funciona](https://docs.docker.com/compose/intro/compose-application-model/).
- Kubernetes. [Conceitos](https://kubernetes.io/docs/concepts/).
- Kubernetes. [Componentes do Kubernetes](https://kubernetes.io/docs/concepts/overview/components/).
- Kubernetes. [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/).
- Kubernetes. [Services](https://kubernetes.io/docs/concepts/services-networking/service/).
- Kubernetes. [Traduzir um arquivo Compose para recursos Kubernetes](https://kubernetes.io/docs/tasks/configure-pod-container/translate-compose-kubernetes/).
- Kompose. [User Guide](https://kompose.io/user-guide/).
