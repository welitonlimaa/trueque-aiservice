from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # OpenAI
    OPENAI_API_KEY: str

    # Models
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    CHAT_MODEL: str = "gpt-4o-mini"
    EMBEDDING_DIMS: int = 1536

    # Elasticsearch
    ELASTICSEARCH_URL: str = "http://elasticsearch:9200"
    ELASTICSEARCH_TOP_K: int = 5
    ELASTICSEARCH_MIN_SCORE: float = 0.4

    # RAG
    MAX_CONTEXT_TOKENS: int = 3000
    SYSTEM_PROMPT: str = (
        "Você é um assistente inteligente e prestativo. "
        "Responda às perguntas do usuário com base no contexto fornecido. "
        "Se a informação não estiver no contexto, diga que não sabe. "
        "Seja claro, objetivo e preciso nas respostas. "
        "Responda sempre no mesmo idioma da pergunta do usuário."
        "Se a pergunta for sobre item retorne apenas o que for relevante dentro do contexto do pedido."
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
