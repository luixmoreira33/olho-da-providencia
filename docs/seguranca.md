# Segurança — Olho da Providência

## Autenticação
- JWT local (HS256).
- Segredo via `JWT_SECRET` (nunca hardcoded em produção).
- Roles: `viewer`, `editor`, `admin`, `advanced`.
- Conexões (hosts de banco/redis/rabbitmq) exigem role avançada.

## Hardening aplicado
- Headers de segurança (`X-Content-Type-Options`, `X-Frame-Options`, etc.).
- Rate limit básico por IP (100 req/min).
- CORS restrito (ajustar em produção).
- Credenciais das fontes sempre read-only.
- Mascaramento de dados sensíveis antes de enviar à IA.

## Policies mínimas (exemplos)
- **Kubernetes**: Role `view` em deployments, pods, services no namespace.
- **AWS**: `ec2:Describe*`, `ecs:Describe*`, `ecs:List*`.
- **Elasticsearch**: permissão de leitura no index pattern.
- **Dynatrace**: token com scope `problems.read` + `entities.read`.

## Checklist
- [ ] `JWT_SECRET` longo e aleatório
- [ ] Tokens de fontes com menor privilégio possível
- [ ] CORS limitado aos domínios reais
- [ ] Logs não contêm segredos
- [ ] Banco SQLite com permissões restritas no host
