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

## Auditoria
- Todas as ações administrativas devem chamar `log_audit(username, action, resource, details)`.
- Tabela `audit_log` registra quem fez o quê e quando.

## OIDC / SSO
- Estrutura pronta em `backend/oidc.py`.
- Ative com `OIDC_ENABLED=true`, `OIDC_ISSUER` e `OIDC_CLIENT_ID`.
- Integração completa com JWKS fica como evolução (biblioteca já disponível via python-jose).

## Cobertura
- Testes unitários: circuit breaker, auth, DB.
- Testes de integração: agregação com fontes mockadas.
- Meta mínima de 70% no motor de status e conectores atingida nos módulos críticos.
