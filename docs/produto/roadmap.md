# Roadmap — Olho da Providência

## MoSCoW (v1.0)

### Must Have
- Conectores resilientes (timeout, circuit breaker, estado "Desconhecido")
- Mapeamento configurável de aplicações entre as 6 fontes
- Motor de status configurável (thresholds por app)
- Cache robusto + coleta em background
- Painel de administração visual (mostrar/ocultar, mapear, testar conexão)
- Detalhes destacados de EC2/ECS no frontend
- Deep links para Kibana, Dynatrace, AWS Console, consoles K8s
- Timeline / histórico de mudanças de status
- Análise de IA com agrupamento de erros e mascaramento de dados sensíveis
- Autenticação (local + OIDC) e RBAC básico
- Docker + docker-compose funcional em modo demo
- Documentação e .env.example completo

### Should Have
- Modo TV/NOC
- Wizard de primeiro uso
- Modo escuro
- Helm charts / manifests para OKD e EKS
- CI/CD básico

### Could Have
- Alertas externos (Slack/Teams)
- SLOs por aplicação
- White-label básico
- Multi-tenant

### Won't Have (v1.0)
- Suporte a Azure/GCP
- Integração nativa com PagerDuty/Opsgenie
- Editor visual de regras complexas

## Fases
1. **Fase 0 (atual):** Descoberta, visão, arquitetura, plano.
2. **Fase 1:** Fundação (conectores, mapeamento, cache, persistência, auth, Docker/CI).
3. **Fase 2:** Experiência (admin visual, cards, deep links, timeline, IA, modo TV).
4. **Fase 3:** Qualidade e Segurança.
5. **Fase 4:** Produto e Mercado (docs, demo, material comercial).

## Premissas
- Self-hosted como modelo principal inicial.
- Credenciais das fontes sempre read-only.
- Fallback mockado preservado para demo e desenvolvimento.
- Identificação de apps via labels/tags configuráveis + correção manual.
