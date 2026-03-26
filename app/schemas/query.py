from pydantic import BaseModel, Field
from typing import Optional, List


class QueryRequest(BaseModel):
    index: str = Field(..., min_length=1, max_length=30, description="index")
    question: str = Field(
        ..., min_length=1, max_length=2000, description="Pergunta do usuário"
    )
    top_k: Optional[int] = Field(
        default=None, ge=1, le=20, description="Número de documentos a recuperar"
    )
    min_score: Optional[float] = Field(
        default=None, ge=1.0, le=2.0, description="Score mínimo de similaridade"
    )
    filters: Optional[dict] = Field(
        default=None, description="Filtros opcionais (category, condition, type)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "index": "faq",
                "question": "Quais são os requisitos para aprovação?",
                "top_k": 5,
                "min_score": 0.0,
                "filters": {"category": "regulamento"},
            }
        }
    }


class SourceDocument(BaseModel):
    text: str
    category: Optional[str] = None
    condition: Optional[str] = None
    type: Optional[str] = None
    score: float


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceDocument]
    question: str
    model: str
    tokens_used: Optional[int] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "answer": "Com base no contexto fornecido...",
                "sources": [
                    {
                        "text": "Trecho relevante do documento...",
                        "category": "regulamento",
                        "score": 0.92,
                    }
                ],
                "question": "Quais são os requisitos para aprovação?",
                "model": "gpt-4o-mini",
                "tokens_used": 512,
            }
        }
    }


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
