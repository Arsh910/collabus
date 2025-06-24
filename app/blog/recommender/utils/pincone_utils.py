from pinecone import Pinecone, ServerlessSpec
from typing import List, Tuple
import numpy as np

PINECONE_API_KEY = (
    "pcsk_1Yv1A_GhaHxPzWThSDKXVw27ABMQUmjTSnWHd8yqXhrRwhRe8LLhLQifAE9UuQJACTnJQ"
)
pc = Pinecone(api_key=PINECONE_API_KEY)


def get_pinecone_index(index_name: str, dimension: int = 384, metric: str = "cosine"):
    existing_indexes = [idx["name"] for idx in pc.list_indexes()]
    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric=metric,
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
    return pc.Index(index_name)


def upsert_vectors(index, vectors: List[Tuple[str, np.ndarray]], namespace: str = ""):
    formatted = [{"id": str(_id), "values": vec} for _id, vec in vectors]
    if vectors:
        index.upsert(vectors=formatted, namespace=namespace)


def fetch_vectors_by_ids(index, ids):
    response = index.fetch(ids=ids)
    return response.vectors if response and response.vectors else {}
