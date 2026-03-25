import json
import os
import requests
from openai import OpenAI

ELASTIC_BASE_URL = os.environ["ELASTICSEARCH_URL"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

INDEX_NAME = "faq"

OPENAI_EMBEDDING_MODEL = os.environ.get(
    "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
)

client = OpenAI(api_key=OPENAI_API_KEY)


# =========================
# EMBEDDING
# =========================
def generate_embedding(text):
    response = client.embeddings.create(input=text, model=OPENAI_EMBEDDING_MODEL)
    return response.data[0].embedding


# =========================
# INDEX DOC
# =========================
def create_index_if_not_exists():
    url = f"{ELASTIC_BASE_URL}/{INDEX_NAME}"

    res = requests.get(url)

    if res.status_code == 200:
        print(f"Index '{INDEX_NAME}' já existe.")
        return

    print(f"Criando index '{INDEX_NAME}'...")

    mapping = {
        "mappings": {
            "properties": {
                "question": {"type": "text"},
                "answer": {"type": "text"},
                "text": {"type": "text"},
                "type": {"type": "keyword"},
                "embedding": {
                    "type": "dense_vector",
                    "dims": 1536,  # compatível com text-embedding-3-small
                    "index": True,
                    "similarity": "cosine",
                },
            }
        }
    }

    res = requests.put(url, json=mapping)

    if res.status_code not in [200, 201]:
        raise Exception(f"Erro ao criar índice: {res.text}")

    print("Index criado com sucesso.")


# =========================
# TRANSFORM
# =========================
def parse_markdown_faq(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    faqs = []
    current_question = None
    current_answer = []

    for line in lines:
        line = line.strip()

        # Pergunta (###)
        if line.startswith("### "):
            if current_question:
                faqs.append(
                    {
                        "question": current_question,
                        "answer": " ".join(current_answer).strip(),
                    }
                )

            current_question = line.replace("### ", "").strip()
            current_answer = []

        else:
            if current_question:
                current_answer.append(line)

    if current_question:
        faqs.append(
            {"question": current_question, "answer": " ".join(current_answer).strip()}
        )

    return faqs


def transform_faq(faq):
    text = f"""
    Pergunta: {faq['question']}
    Resposta: {faq['answer']}
    """

    return {
        "question": faq["question"],
        "answer": faq["answer"],
        "text": text,
        "type": "faq",
    }


# =========================
# HANDLER
# =========================
def lambda_handler(event, context):
    print("Iniciando ingestão de FAQ...")

    create_index_if_not_exists()

    file_path = "./data/trueque_faq.md"
    faqs = parse_markdown_faq(file_path)

    print(f"{len(faqs)} FAQs encontradas.")

    for faq in faqs:
        doc = transform_faq(faq)

        try:
            embedding = generate_embedding(doc["text"])
            doc["embedding"] = embedding

            res = requests.post(
                f"{ELASTIC_BASE_URL}/{INDEX_NAME}/_doc", json=doc, timeout=5
            )

            if res.status_code not in [200, 201]:
                print("Erro ao indexar:", res.text)

        except Exception as e:
            print("Erro:", str(e))

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "FAQ ingerido com sucesso"}),
    }


if __name__ == "__main__":
    lambda_handler({}, {})
