# Painel de Status Unificado (OKD / EKS / ELK / Dynatrace)

Dashboard prático para desenvolvedores acompanharem o status por aplicação de forma objetiva.

## O que você precisa fazer

1. Copie o exemplo de configuração:
   ```bash
   cd backend
   cp .env.example .env
   ```
2. Edite o `.env` com os dados reais de conexão (kubeconfigs, URLs, tokens, etc.).
3. Instale as dependências e rode.

Pronto. Se alguma fonte não estiver configurada ou falhar, o sistema usa dados mockados (controlado por `USE_MOCK_IF_UNCONFIGURED`) e continua funcionando.

## Como rodar

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Documentação: http://localhost:8000/docs  
Status das fontes: http://localhost:8000/

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Acesse http://localhost:5173

## Variáveis de conexão (resumo)

| Variável              | Descrição                                      | Exemplo                          |
|-----------------------|------------------------------------------------|----------------------------------|
| `OKD_KUBECONFIG`      | Caminho do kubeconfig do OKD                   | `/home/user/.kube/okd-config`    |
| `OKD_CONTEXT`         | Contexto no kubeconfig                         | `okd-prod`                       |
| `OKD_NAMESPACE`       | Namespace padrão                               | `production`                     |
| `OKD_APP_LABEL`       | Label que identifica a app                     | `app`                            |
| `EKS_KUBECONFIG`      | Caminho do kubeconfig do EKS                   | `/home/user/.kube/eks-config`    |
| `ELK_URL`             | URL do Elasticsearch                           | `https://es:9200`                |
| `ELK_API_KEY`         | API Key (preferível)                           | `...`                            |
| `ELK_SERVICE_FIELD`   | Campo que contém o nome da app nos logs        | `service.name` ou `kubernetes.labels.app` |
| `DYNATRACE_URL`       | URL do ambiente Dynatrace                      | `https://xxx.live.dynatrace.com` |
| `DYNATRACE_TOKEN`     | API Token                                      | `dt0c01....`                     |

## Como as apps são identificadas

- **Kubernetes (OKD/EKS)**: pelo valor da label definida em `OKD_APP_LABEL` / `EKS_APP_LABEL` (padrão `app`).
- **ELK**: pelo campo definido em `ELK_SERVICE_FIELD`.
- **Dynatrace**: matching por nome do serviço/entidade afetada nos problemas abertos.

Se quiser uma lista fixa de apps, use `APP_LIST=app1,app2,app3`.

## Personalização do frontend

O código está em `frontend/src/App.jsx`. Os cards, cores, filtros e layout são fáceis de ajustar.
