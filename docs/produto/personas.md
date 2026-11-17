# Personas — Olho da Providência

## 1. Desenvolvedor de Squad (usuário principal)
- **Objetivo:** saber rapidamente se "a minha app" está saudável antes de abrir ticket ou chamar alguém.
- **Dor:** abre 5 ferramentas, perde tempo correlacionando, às vezes nem sabe onde olhar.
- **Sucesso:** abre o painel, vê o card da app, entende o problema e clica no deep link já filtrado.

## 2. Tech Lead / Líder técnico
- **Objetivo:** visão do estado das apps do time + identificar padrões de degradação.
- **Dor:** depende de reports manuais ou de cada dev abrir as ferramentas.
- **Sucesso:** dashboard com filtro por time/ambiente e tendência.

## 3. SRE / Plantão
- **Objetivo:** triagem rápida de incidentes e redução de MTTD.
- **Dor:** recebe alertas genéricos e precisa investigar em várias ferramentas.
- **Sucesso:** modo TV/NOC + timeline + links diretos + resumo de IA.

## 4. Gestor / Engenharia
- **Objetivo:** visibilidade de saúde do portfólio de aplicações e redução de custo operacional.
- **Dor:** falta de métricas claras de tempo de diagnóstico e disponibilidade.
- **Sucesso:** métricas de adoção e tempo de resolução.

## Jornadas principais
1. **Verificação diária** — Dev abre o painel → vê status das apps do time → se algo estiver amarelo/vermelho, expande e clica no link.
2. **Investigação de incidente** — SRE abre app crítica → vê timeline + resumo de IA + deep links lado a lado.
3. **Configuração inicial** — Admin conecta fontes via wizard → confirma mapeamento de apps → ajusta thresholds.
4. **Onboarding de novo membro** — Novo dev acessa o painel e entende o estado do sistema sem treinamento longo.
