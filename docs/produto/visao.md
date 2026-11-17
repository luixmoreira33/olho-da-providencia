# Visão do Produto — Olho da Providência

## O que é
Painel unificado de status **por aplicação** que responde, em menos de 5 segundos, à pergunta mais importante de um desenvolvedor: **"minha app está bem?"**

Consolida OKD, EKS, ELK, Dynatrace, EC2 e ECS em uma única visão objetiva, com análise de IA e links diretos para a ferramenta de origem.

## Problema que resolve
Hoje o desenvolvedor precisa abrir 4–6 ferramentas diferentes (console K8s, Kibana, Dynatrace, AWS Console) para entender se uma aplicação está saudável e onde está o problema. Isso aumenta MTTD/MTTR, gera troca de contexto e dificulta o onboarding de novos membros do time.

## Proposta de valor
- **Velocidade:** veredito (Healthy / Warning / Critical) + causa provável em 5 segundos.
- **Menos contexto:** um clique no card leva ao detalhe; segundo clique abre a ferramenta de origem já filtrada.
- **Confiança:** fonte fora do ar aparece como "Desconhecido", nunca como verde silencioso.
- **Onboarding:** novo dev entende o estado do sistema em minutos, sem conhecer todas as ferramentas.
- **Foco no time:** visão por aplicação (não por infraestrutura crua).

## Métricas de sucesso
- Tempo médio para identificar se uma app está com problema (meta: < 10s).
- Número de ferramentas abertas por incidente (meta: redução de 60%+).
- Adoção diária pelo time de desenvolvimento.
- Redução de escalonamentos desnecessários ao SRE.

## Público-alvo
Times de desenvolvimento e SRE que operam aplicações em Kubernetes (OKD/EKS) + observabilidade (ELK/Dynatrace) + AWS (EC2/ECS).

## Diferenciais
- Agrupamento nativo por aplicação (não por recurso).
- Análise de IA que "mastiga" os logs e correlaciona sinais.
- Configuração guiada e admin visual (sem editar arquivos no dia a dia).
- Pronto para self-hosted e multi-ambiente.
