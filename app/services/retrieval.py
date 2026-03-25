import logging
import httpx
from typing import Optional
from app.core.config import settings
from app.schemas.query import SourceDocument

logger = logging.getLogger(__name__)


class ElasticsearchService:
    def __init__(self):
        self.base_url = settings.ELASTICSEARCH_URL
        self.timeout = httpx.Timeout(10.0)

    def _build_query(
        self,
        query: str,
        embedding: list[float],
        top_k: int,
        min_score: float,
        filters: Optional[dict] = None,
    ) -> dict:
        """Monta query híbrida (texto + embedding)."""

        base_query = {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ["text", "category^3"],
                        }
                    }
                ]
            }
        }

        # aplica filtros se existirem
        if filters:
            filter_clauses = []
            for field, value in filters.items():
                if value is not None:
                    filter_clauses.append({"term": {field: value}})

            if filter_clauses:
                base_query = {
                    "bool": {
                        "must": [base_query],
                        "filter": filter_clauses,
                    }
                }

        return {
            "size": top_k,
            "min_score": min_score,
            "_source": ["text", "category", "condition", "type"],
            "query": {
                "script_score": {
                    "query": base_query,
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                        "params": {"query_vector": embedding},
                    },
                }
            },
        }

    async def search(
        self,
        index: str,
        query: str,
        embedding: list[float],
        top_k: Optional[int] = None,
        min_score: Optional[float] = None,
        filters: Optional[dict] = None,
    ) -> list[SourceDocument]:
        """Executa busca híbrida no Elasticsearch."""

        top_k = top_k or settings.ELASTICSEARCH_TOP_K
        min_score = min_score or settings.ELASTICSEARCH_MIN_SCORE

        url = f"{self.base_url}/{index}/_search"

        enriched_query = f"{query}"

        query_body = self._build_query(
            enriched_query,
            embedding,
            top_k,
            min_score,
            filters,
        )

        logger.info(
            f"Buscando no Elasticsearch — index: {index}, top_k: {top_k}, min_score: {min_score}"
        )

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    url,
                    json=query_body,
                    headers={"Content-Type": "application/json"},
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.error(
                    f"Erro HTTP do Elasticsearch: {e.response.status_code} — {e.response.text}"
                )
                raise RuntimeError(
                    f"Elasticsearch retornou erro {e.response.status_code}: {e.response.text}"
                )
            except httpx.RequestError as e:
                logger.error(f"Erro de conexão com Elasticsearch: {e}")
                raise RuntimeError(
                    f"Não foi possível conectar ao Elasticsearch: {str(e)}"
                )

        data = response.json()
        hits = data.get("hits", {}).get("hits", [])

        logger.info(f"{len(hits)} documento(s) recuperado(s)")

        documents = []
        for hit in hits:
            source = hit.get("_source", {})
            score = hit.get("_score", 0.0)

            documents.append(
                SourceDocument(
                    text=source.get("text", ""),
                    category=source.get("category"),
                    condition=source.get("condition"),
                    type=source.get("type"),
                    score=round(score, 4),
                )
            )

        return documents
