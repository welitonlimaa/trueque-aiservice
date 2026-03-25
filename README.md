# RAG AI Service

Serviço de **Retrieval-Augmented Generation (RAG)** construído com **FastAPI + OpenAI + Elasticsearch**.

---

## Arquitetura do Pipeline

```
User pergunta
     ↓
POST /api/v1/query
     ↓
EmbeddingService       →  text-embedding-3-small (1536 dims)
     ↓
ElasticsearchService   →  KNN cosine similarity search
     ↓
ContextBuilder         →  Monta contexto com limite de tokens
     ↓
GenerationService      →  gpt-4o-mini
     ↓
QueryResponse          →  answer + sources + tokens_used
```

---

## Estrutura do Projeto

```
rag-service/
├── main.py                     
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
│
├── app/
│   ├── api/
│   │   └── routes.py           # Endpoints REST
│   ├── core/
│   │   └── config.py           # Configurações via env vars
│   ├── schemas/
│   │   └── query.py            # Modelos Pydantic
│   └── services/
│       ├── embedding.py        # Geração de embeddings (OpenAI)
│       ├── retrieval.py        # Busca no Elasticsearch (KNN)
│       ├── context.py          # Montagem do contexto
│       ├── generation.py       # Geração de resposta (OpenAI)
│       └── rag.py              # Orquestrador do pipeline
```

---

## Configuração

### 1. Variáveis de Ambiente

Copie o arquivo de exemplo e preencha:

```bash
cp .env.example .env
```

| Variável | Padrão | Descrição |
|---|---|---|
| `OPENAI_API_KEY` | — | **Obrigatório** |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Modelo de embedding |
| `CHAT_MODEL` | `gpt-4o-mini` | Modelo de geração |
| `EMBEDDING_DIMS` | `1536` | Dimensões do embedding |
| `ELASTICSEARCH_URL` | `http://elasticsearch:9200` | URL do ES |
| `ELASTICSEARCH_TOP_K` | `5` | Documentos recuperados |
| `ELASTICSEARCH_MIN_SCORE` | `0.6` | Score mínimo de similaridade |
| `MAX_CONTEXT_TOKENS` | `3000` | Limite de tokens no contexto |

---

## Execução

### Com Docker Compose (recomendado)

```bash
# Sobe o serviço + Elasticsearch
docker-compose up -d
```

### Local (desenvolvimento)

```bash
# Instala dependências
pip install -r requirements.txt

# Sobe o servidor
uvicorn main:app --reload --port 8000
```

---

## API

### `POST /api/v1/query`

**Request:**

```json
{
  "index": "faq",
  "question": "Como acontece a troca de itens?",
  "top_k": 5,
  "min_score": 0.7
}
```

### `GET /health`

```json
{ "status": "ok", "service": "RAG AI Service" }
```

---

## Exemplo com cURL

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "index": "faq",
    "question": "Como acontece a troca de itens?",
    "top_k": 5,
    "min_score": 0.7
  }'
```