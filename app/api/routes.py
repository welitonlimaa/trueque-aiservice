import logging
from fastapi import APIRouter, HTTPException, Depends
from functools import lru_cache

from app.schemas.query import QueryRequest, QueryResponse
from app.services.rag import RAGService

logger = logging.getLogger(__name__)

router = APIRouter()


@lru_cache()
def get_rag_service() -> RAGService:
    return RAGService()


@router.post(
    "/query",
    response_model=QueryResponse,
    summary="Consultar a base de conhecimento via RAG",
    description="Recebe uma pergunta, busca documentos relevantes e retorna resposta gerada pelo LLM.",
)
async def query(
    request: QueryRequest,
    rag: RAGService = Depends(get_rag_service),
):
    try:
        logger.info(
            f"POST /query — pergunta: '{request.index} - {request.question[:80]}'"
        )
        response = await rag.query(request)
        return response

    except RuntimeError as e:
        logger.error(f"Erro no pipeline RAG: {e}")
        raise HTTPException(status_code=502, detail=str(e))

    except Exception as e:
        logger.exception(f"Erro inesperado: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no servidor")
