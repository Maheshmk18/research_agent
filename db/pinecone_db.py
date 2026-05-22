import os
from hashlib import sha256

from dotenv import load_dotenv
from pinecone import Pinecone


load_dotenv()


PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "research-reports")
PINECONE_EMBED_MODEL = os.getenv("PINECONE_EMBED_MODEL", "llama-text-embed-v2")


pc = Pinecone(api_key=PINECONE_API_KEY) if PINECONE_API_KEY else None


def get_index():
    if not pc:
        raise RuntimeError("Pinecone API key is missing")
    try:
        return pc.Index(PINECONE_INDEX_NAME)
    except Exception as exc:
        raise RuntimeError(
            f'Pinecone index "{PINECONE_INDEX_NAME}" was not found for the configured API key. '
            "Create the index in Pinecone or update PINECONE_INDEX_NAME in .env to match an existing index."
        ) from exc


def _hash_embed_text(text: str, dimension: int = 1536):
    values = [0.0] * dimension
    words = text.lower().split()

    if not words:
        return values

    for word in words:
        digest = sha256(word.encode("utf-8")).digest()
        slot = int.from_bytes(digest[:4], "big") % dimension
        weight = ((digest[4] / 255.0) * 2.0) - 1.0
        values[slot] += weight

    norm = sum(value * value for value in values) ** 0.5
    if norm:
        values = [value / norm for value in values]

    return values


def embed_text(text: str, input_type: str = "passage"):
    try:
        if not pc:
            return _hash_embed_text(text)

        response = pc.inference.embed(
            model=PINECONE_EMBED_MODEL,
            inputs=[text],
            parameters={"input_type": input_type, "truncate": "END"},
        )

        data = getattr(response, "data", None) or response.get("data", [])
        if not data:
            return _hash_embed_text(text)

        first = data[0]
        values = getattr(first, "values", None) or first.get("values")
        return values or _hash_embed_text(text)
    except Exception:
        return _hash_embed_text(text)


def save_report_vector(
    vector_id: str,
    values: list[float],
    topic: str,
    mongo_id: str,
    status: str,
    verified: str,
    word_count: int,
    created_at: str,
):
    metadata = {
        "topic": topic,
        "mongo_id": mongo_id,
        "status": status,
        "verified": verified,
        "word_count": word_count,
        "created_at": created_at,
    }
    try:
        index = get_index()
        return index.upsert(vectors=[{"id": vector_id, "values": values, "metadata": metadata}])
    except Exception as exc:
        if PINECONE_INDEX_NAME in str(exc) and "not found" in str(exc).lower():
            raise RuntimeError(
                f'Pinecone index "{PINECONE_INDEX_NAME}" does not exist. '
                "Create it in Pinecone before saving report vectors."
            ) from exc
        raise


def search_report_vectors(values: list[float], top_k: int = 5):
    try:
        index = get_index()
        return index.query(vector=values, top_k=top_k, include_metadata=True)
    except Exception as exc:
        if PINECONE_INDEX_NAME in str(exc) and "not found" in str(exc).lower():
            raise RuntimeError(
                f'Pinecone index "{PINECONE_INDEX_NAME}" does not exist. '
                "Create it in Pinecone before searching report vectors."
            ) from exc
        raise


def get_report_vector(vector_id: str):
    try:
        index = get_index()
        return index.fetch(ids=[vector_id])
    except Exception as exc:
        if PINECONE_INDEX_NAME in str(exc) and "not found" in str(exc).lower():
            raise RuntimeError(
                f'Pinecone index "{PINECONE_INDEX_NAME}" does not exist. '
                "Create it in Pinecone before fetching report vectors."
            ) from exc
        raise


def delete_report_vector(vector_id: str):
    try:
        index = get_index()
        return index.delete(ids=[vector_id])
    except Exception as exc:
        if PINECONE_INDEX_NAME in str(exc) and "not found" in str(exc).lower():
            raise RuntimeError(
                f'Pinecone index "{PINECONE_INDEX_NAME}" does not exist. '
                "Create it in Pinecone before deleting report vectors."
            ) from exc
        raise
