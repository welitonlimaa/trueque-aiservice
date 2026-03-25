import logging

from app.services.embedding import EmbeddingService
from app.services.retrieval import ElasticsearchService
from app.services.context import build_context
from app.services.generation import GenerationService
from app.schemas.query import QueryRequest, QueryResponse
from app.core.config import settings

logger = logging.getLogger(__name__)


class RAGService:
    """
    Orquestra o pipeline RAG completo.
    """

    def __init__(self):
        self.embedder = EmbeddingService()
        self.retriever = ElasticsearchService()
        self.generator = GenerationService()

    async def query(self, request: QueryRequest) -> QueryResponse:
        question = request.question.strip()
        logger.info(f"[RAG] Pergunta recebida: '{question[:100]}'")

        # Gera embedding da pergunta
        embedding = await self.embedder.generate(question)

        # Busca documentos relevantes no Elasticsearch
        documents = await self.retriever.search(
            index=request.index,
            query=question,
            embedding=embedding,
            top_k=request.top_k,
            min_score=request.min_score,
            filters=request.filters,
        )

        if not documents:
            logger.warning(f"{len(documents)}")
            logger.warning("[RAG] Nenhum documento relevante encontrado")

        # Monta contexto
        context = build_context(documents)

        # Gera resposta
        answer, tokens_used = await self.generator.generate(
            question=question,
            context=context,
        )

        logger.info(
            f"[RAG] Pipeline concluído. Documentos: {len(documents)}, Tokens: {tokens_used}"
        )

        return QueryResponse(
            answer=answer,
            sources=documents,
            question=question,
            model=settings.CHAT_MODEL,
            tokens_used=tokens_used,
        )
