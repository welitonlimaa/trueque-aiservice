import json
import os
import requests
from openai import OpenAI

API_URL = os.environ["API_URL"]
ELASTIC_URL = os.environ["ELASTICSEARCH_URL"]
INDEX_NAME = "itens"
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
OPENAI_EMBEDDING_MODEL = os.environ.get(
    "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
)

client = OpenAI(api_key=OPENAI_API_KEY)


mapping = {
    "mappings": {
        "properties": {
            "text": {"type": "text"},
            "category": {"type": "keyword"},
            "condition": {"type": "keyword"},
            "type": {"type": "keyword"},
            "id": {"type": "keyword"},
            "link": {"type": "keyword"},
            "embedding": {
                "type": "dense_vector",
                "dims": 1536,
                "index": True,
                "similarity": "cosine",
            },
        }
    }
}


# =========================
# INDEX
# =========================
def create_index_if_not_exists():
    url = f"{ELASTIC_URL}/{INDEX_NAME}"

    check = requests.head(url)

    if check.status_code == 200:
        print(f"Index '{INDEX_NAME}' já existe")
        return

    print(f"Criando index '{INDEX_NAME}'...")

    res = requests.put(url, json=mapping)

    if res.status_code not in [200, 201]:
        raise Exception(f"Erro ao criar index: {res.text}")

    print("Index criado com sucesso")


# =========================
# EMBEDDING
# =========================
def generate_embedding(text):
    response = client.embeddings.create(input=text, model=OPENAI_EMBEDDING_MODEL)
    return response.data[0].embedding


# =========================
# TRANSFORM
# =========================
def transform_product(p):
    text = f"""
    item: {p.get('title', '')}
    id: {p.get("id"), ''}
    Descrição: {p.get('description', '')}
    Categoria: {p.get('category', '')}
    Condição: {p.get('condition', '')}
    link: https://truequeapp.welitonlima.com/listings/{p.get("id"), ''}
    """

    return {
        "text": text,
        "id": p.get("id"),
        "link": f"https://truequeapp.welitonlima.com/listings/{p.get("id")}",
        "category": p.get("category"),
        "condition": p.get("condition"),
        "type": "item",
    }


# =========================
# INDEX DOC
# =========================
def index_item(doc_id, doc):
    url = f"{ELASTIC_URL}/{INDEX_NAME}/_doc/{doc_id}"

    res = requests.put(url, json=doc)

    if res.status_code not in [200, 201]:
        print(f"Erro ao indexar {doc_id}: {res.text}")
    else:
        print(f"item {doc_id} indexado")


# =========================
# HANDLER
# =========================
def lambda_handler(event, context):
    print("Iniciando ingestão...")

    create_index_if_not_exists()

    response = requests.get(API_URL, timeout=10)
    itens = response.json()

    for p in itens:
        try:
            doc_id = str(p.get("id"))

            doc = transform_product(p)

            embedding = generate_embedding(doc["text"])
            doc["embedding"] = embedding

            index_item(doc_id, doc)

        except Exception as e:
            print(f"Erro no iten {p.get('id')}: {str(e)}")

    return {"statusCode": 200, "body": json.dumps({"message": "Ingestão concluída"})}


if __name__ == "__main__":
    lambda_handler({}, {})
