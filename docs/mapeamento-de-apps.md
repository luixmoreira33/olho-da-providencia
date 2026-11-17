# Mapeamento de Aplicações — Guia Inicial

## Problema
A mesma aplicação aparece com nomes/identificadores diferentes nas 6 fontes:
- K8s (OKD/EKS): label `app` ou `app.kubernetes.io/name`
- ELK: campo `service.name`, `kubernetes.labels.app`, etc.
- Dynatrace: nome do serviço/entidade
- EC2: tag `Name` ou `app`
- ECS: nome do service / cluster

## Abordagem (v1.0)
1. **Auto-descoberta:** o sistema lista recursos de cada fonte e sugere agrupamentos por similaridade de nome.
2. **Correção manual:** na tela de administração o usuário vincula recursos órfãos a uma aplicação.
3. **Regras configuráveis:** labels e campos são configuráveis por fonte (já existem no `.env` e serão expostos na UI).

## Recursos órfãos
Qualquer recurso sem app associada aparece na admin para o usuário decidir se cria uma nova app ou vincula a uma existente.

## Próximos passos
- Implementar o módulo de mapeamento na Fase 1.
- UI de vinculação na Fase 2.
