# Olho da Providência

**O painel que responde “minha app está bem?” em 5 segundos.**

Consolida status de **OKD, EKS, ELK, Dynatrace, EC2 e ECS** por aplicação, com análise de IA, deep links e visão de conexões (perfil avançado).

## Quick Start (modo demo)

```bash
git clone https://github.com/luixmoreira33/olho-da-providencia.git
cd olho-da-providencia
docker compose up --build
```

- Frontend: http://localhost:5173  
- Backend: http://localhost:8000  
- Docs: http://localhost:8000/docs  

Sem nenhuma credencial o painel sobe com dados mockados.

## Configuração real
Copie `backend/.env.example` para `backend/.env` e preencha as fontes.  
Use a aba **Admin** para controlar o que aparece e mapear apps.

## Recursos principais
- Status Healthy / Warning / Critical por app
- Cards expansíveis + deep links
- Análise de IA com mascaramento de dados sensíveis
- Conexões (banco, Redis, RabbitMQ) só para perfil avançado
- Admin visual, modo TV, dark mode, timeline
- Autenticação local + base OIDC
- Helm chart para OKD/EKS

## Documentação
- `docs/produto/` — visão, personas, roadmap
- `docs/arquitetura.md`
- `docs/seguranca.md`
- `docs/comercial/` — posicionamento, preços, one-pager, roteiro de demo, ROI
- `docs/mapeamento-de-apps.md`

## Deploy em Kubernetes
```bash
helm install olho ./helm/olho-da-providencia
```
