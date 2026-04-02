# RAG AI Service

Serviço de **Retrieval-Augmented Generation (RAG)** construído com **FastAPI + OpenAI + Elasticsearch**.

---

## Arquitetura do Pipeline

<img width="1370" height="740" alt="Image" src="https://github.com/user-attachments/assets/f218ed8e-e154-4199-83cb-13670f133ef6" />

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
