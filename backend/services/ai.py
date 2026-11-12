import requests
import logging
from typing import Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Simple in-memory cache: {app_name: (insight, timestamp)}
_ai_cache = {}
CACHE_TTL_MINUTES = 10


class AIInsightClient:
    def __init__(self, enabled: bool, base_url: Optional[str], api_key: Optional[str], model: str):
        self.enabled = enabled and bool(base_url and api_key)
        self.base_url = base_url.rstrip("/") if base_url else None
        self.api_key = api_key
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        } if api_key else {}

        if self.enabled:
            logger.info(f"AI insight client enabled (model: {model})")
        else:
            logger.info("AI insight client disabled or not configured")

    def analyze_errors(self, app_name: str, recent_errors: List[str], error_count: int) -> Optional[str]:
        """Generate a concise, developer-friendly insight from recent errors."""
        if not self.enabled or not recent_errors or error_count < 3:
            return None

        # Check cache
        now = datetime.utcnow()
        if app_name in _ai_cache:
            insight, ts = _ai_cache[app_name]
            if now - ts < timedelta(minutes=CACHE_TTL_MINUTES):
                return insight

        prompt = f"""Você é um assistente de observabilidade para desenvolvedores.

Aplicação: {app_name}
Quantidade de erros na última hora: {error_count}

Erros recentes:
{chr(10).join(f"- {e}" for e in recent_errors[:5])}

Forneça um resumo objetivo e acionável (máximo 4 linhas) em português:
1. O que está acontecendo (resumo)
2. Possível causa raiz
3. O que o desenvolvedor deve verificar primeiro

Seja direto, sem jargão desnecessário e sem inventar informações que não estão nos logs."""

        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "Você resume problemas de logs de forma clara e prática para desenvolvedores."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 250
            }

            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=20
            )
            resp.raise_for_status()
            data = resp.json()
            insight = data["choices"][0]["message"]["content"].strip()

            # Cache it
            _ai_cache[app_name] = (insight, now)
            return insight

        except Exception as e:
            logger.warning(f"AI analysis failed for {app_name}: {e}")
            return None
