import requests
import logging
import re
from typing import Optional, List, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

_ai_cache: Dict[str, tuple] = {}
CACHE_TTL_MINUTES = 10

SENSITIVE_PATTERNS = [
    (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), '[EMAIL]'),
    (re.compile(r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b'), '[CPF]'),
    (re.compile(r'(?i)(token|password|secret|key|authorization)[\s:=]+[^\s]+'), r'\1=[REDACTED]'),
]


def mask_sensitive(text: str) -> str:
    for pattern, repl in SENSITIVE_PATTERNS:
        text = pattern.sub(repl, text)
    return text


class AIInsightClient:
    def __init__(self, enabled: bool, base_url: Optional[str], api_key: Optional[str], model: str):
        self.enabled = enabled and bool(base_url and api_key)
        self.base_url = base_url.rstrip("/") if base_url else None
        self.api_key = api_key
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        } if api_key else {}

    def _group_errors(self, errors: List[str]) -> List[str]:
        """Simple grouping by similarity (first 80 chars)."""
        groups = {}
        for err in errors:
            key = err[:80].strip()
            groups[key] = groups.get(key, 0) + 1
        return [f"{k} (x{v})" for k, v in sorted(groups.items(), key=lambda x: -x[1])]

    def analyze_errors(self, app_name: str, errors: List[str], error_count: int, correlated: Optional[Dict] = None) -> Optional[str]:
        if not self.enabled or not errors:
            return None

        signature = f"{app_name}:{error_count}:{hash(tuple(errors[:5]))}"
        now = datetime.utcnow()
        if signature in _ai_cache:
            insight, ts = _ai_cache[signature]
            if now - ts < timedelta(minutes=CACHE_TTL_MINUTES):
                return insight

        grouped = self._group_errors(errors)
        masked = [mask_sensitive(e) for e in grouped[:8]]

        prompt = f"""Analise de forma objetiva e prática os erros da aplicação "{app_name}".
Erros agrupados (últimos):
{chr(10).join(f'- {e}' for e in masked)}
Total aproximado na última hora: {error_count}

Sinais correlacionados: {correlated or 'nenhum'}

Responda em português, em no máximo 4 linhas:
1. O que está acontecendo
2. Causa provável
3. O que verificar primeiro
4. Impacto estimado
"""

        try:
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 300,
                    "temperature": 0.2,
                },
                timeout=20,
            )
            resp.raise_for_status()
            insight = resp.json()["choices"][0]["message"]["content"].strip()
            _ai_cache[signature] = (insight, now)
            return insight
        except Exception as e:
            logger.warning(f"AI insight failed: {e}")
            return None
