import logging
from app.schemas.query import SourceDocument
from app.core.config import settings

logger = logging.getLogger(__name__)

# 4 chars por token
CHARS_PER_TOKEN = 4


def build_context(documents: list[SourceDocument]) -> str:
    """
    Monta o contexto a ser enviado ao LLM a partir dos documentos recuperados.
    Com limite de tokens.
    """
    if not documents:
        return ""

    max_chars = settings.MAX_CONTEXT_TOKENS * CHARS_PER_TOKEN
    context_parts = []
    total_chars = 0

    for i, doc in enumerate(documents, start=1):
        meta_parts = []
        if doc.category:
            meta_parts.append(f"Categoria: {doc.category}")
        if doc.condition:
            meta_parts.append(f"Condição: {doc.condition}")
        if doc.type:
            meta_parts.append(f"Tipo: {doc.type}")

        meta_str = f" [{', '.join(meta_parts)}]" if meta_parts else ""
        entry = f"[Documento {i}{meta_str}]\n{doc.text.strip()}\n"

        if total_chars + len(entry) > max_chars:
            logger.warning(
                f"Limite de contexto atingido — parando em {i - 1} documento(s)"
            )
            break

        context_parts.append(entry)
        total_chars += len(entry)

    context = "\n".join(context_parts)
    logger.info(
        f"Contexto montado: {len(context_parts)} doc(s), ~{total_chars // CHARS_PER_TOKEN} tokens"
    )
    return context
