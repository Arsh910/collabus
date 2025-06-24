from blog.recommender.embeddings.user_embeddings import (
    compute_and_save_user_embeddings,
)
from blog.recommender.logs.mongo import reads_collection, likes_collection
from blog.recommender.model.model import load_model, load_device

model, tokenizer = load_model()
device = load_device()


def update_user_embeddings():
    compute_and_save_user_embeddings(
        model, tokenizer, device, reads_collection, likes_collection, new_only=True
    )


def update_all_user_embeddings():
    compute_and_save_user_embeddings(
        model, tokenizer, device, reads_collection, likes_collection, new_only=False
    )
