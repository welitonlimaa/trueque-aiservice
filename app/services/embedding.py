import logging
from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.EMBEDDING_MODEL
        self.dims = settings.EMBEDDING_DIMS

    async def generate(self, text: str) -> list[float]:
        """Gera embedding para um texto usando text-embedding-3-small."""
        try:
            text = text.replace("\n", " ").strip()
            logger.info(f"Gerando embedding para: '{text[:80]}...'")

            response = await self.client.embeddings.create(
                model=self.model,
                input=text,
                dimensions=self.dims,
            )

            embedding = response.data[0].embedding
            logger.info(f"Embedding gerado {embedding}")
            logger.info(f"Embedding gerado com {len(embedding)} dimensões")
            return embedding

        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {e}")
            raise RuntimeError(f"Falha ao gerar embedding: {str(e)}")
