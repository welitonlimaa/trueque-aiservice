import logging
from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


class GenerationService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.CHAT_MODEL

    async def generate(self, question: str, context: str) -> tuple[str, int]:
        """
        Gera resposta usando o LLM com base na pergunta e contexto recuperado.
        Retorna (answer, tokens_used).
        """
        if context:
            user_content = f"Contexto:\n{context}\n\n" f"Pergunta: {question}"
        else:
            user_content = (
                f"Não foram encontrados documentos relevantes no contexto.\n\n"
                f"Pergunta: {question}"
            )

        messages = [
            {"role": "system", "content": settings.SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]

        logger.info(f"Chamando modelo {self.model}...")

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=1024,
            )

            answer = response.choices[0].message.content.strip()
            tokens_used = response.usage.total_tokens if response.usage else None

            logger.info(f"Resposta gerada. Tokens usados: {tokens_used}")
            return answer, tokens_used

        except Exception as e:
            logger.error(f"Erro ao chamar o modelo: {e}")
            raise RuntimeError(f"Falha na geração da resposta: {str(e)}")
