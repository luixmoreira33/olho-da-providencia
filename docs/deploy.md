# Deploy — Olho da Providência

## Docker Compose (recomendado para começar)
```bash
docker compose up --build
```

## Helm (OKD / EKS)
```bash
helm install olho ./helm/olho-da-providencia \
  --set env.JWT_SECRET=$(openssl rand -hex 32)
```

### ServiceAccount e RBAC
Crie um ServiceAccount com permissões **somente leitura** nos namespaces desejados (deployments, pods, services).

## Variáveis importantes
- `JWT_SECRET` — obrigatório em produção
- `USE_MOCK_IF_UNCONFIGURED=true` — útil para demo
- Credenciais das fontes via env ou secrets do Kubernetes
