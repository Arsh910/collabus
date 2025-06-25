import numpy as np
from tqdm import tqdm
from blog.models import Blogs
from django.contrib.auth import get_user_model
from blog.recommender.utils.pincone_utils import (
    get_pinecone_index,
    upsert_vectors,
)
from blog.recommender.logs.mongo import mark_blog_as_uploaded, fetch_existing_blog_ids
import torch

BLOG_INDEX_NAME = "blog-embeddings"
AUTHOR_INDEX_NAME = "author-embeddings"


def embed_texts(texts, model, tokenizer, device):
    model.eval()
    all_embeddings = []

    batch_size = 16
    total_batches = (len(texts) + batch_size - 1) // batch_size

    with torch.no_grad():
        for i in tqdm(
            range(0, len(texts), batch_size),
            desc="🔢 Embedding texts",
            total=total_batches,
        ):
            batch = texts[i : i + batch_size]
            inputs = tokenizer(
                batch, return_tensors="pt", padding=True, truncation=True
            ).to(device)
            if (
                "token_type_ids" in inputs
                and "token_type_ids" not in model.forward.__code__.co_varnames
            ):
                inputs.pop("token_type_ids")

            embeddings = model(**inputs)
            all_embeddings.append(embeddings.cpu().numpy())

    return np.vstack(all_embeddings)


def compute_blog_embeddings(blogs, model, tokenizer, device):
    print(f"🧠 Embedding {len(blogs)} blogs...")
    texts = [blog.text for blog in tqdm(blogs, desc="📄 Collecting blog texts")]
    ids = [str(blog.id) for blog in blogs]
    embeddings = embed_texts(texts, model, tokenizer, device)
    return list(zip(ids, embeddings))


def compute_and_save_blog_embeddings(model, tokenizer, device, new_only=False):
    print("📥 Retrieving blog list...")
    blog_index = get_pinecone_index(BLOG_INDEX_NAME)

    if new_only:
        known_ids = fetch_existing_blog_ids()
        blogs = Blogs.objects.exclude(id__in=known_ids)

        print(f"🆕 Found {blogs.count()} new blogs to embed.")
    else:
        blogs = Blogs.objects.all()
        print(f"🔄 Full refresh: {blogs.count()} blogs to embed.")

    if not blogs.exists():
        print("⚠️ No blogs to embed.")
        return

    blog_emb_pairs = compute_blog_embeddings(blogs, model, tokenizer, device)
    blog_vectors = [(bid, emb.tolist()) for bid, emb in blog_emb_pairs]

    print(f"🔄 Saving blog embeddings logs")
    for blog_id, _ in blog_emb_pairs:
        mark_blog_as_uploaded(blog_id)
    print(f"✅ Saved blog embeddings logs")
    

    print("⬆️ Uploading blog embeddings to Pinecone...")
    upsert_vectors(blog_index, blog_vectors)
    print(f"✅ Uploaded {len(blog_vectors)} blog embeddings.")

    if not new_only:
        print("🧾 Computing author embeddings (full update)...")
        compute_and_save_author_embeddings(blog_emb_pairs)


def compute_author_embeddings(blog_emb_pairs):
    blog_id_to_vec = {bid: emb for bid, emb in blog_emb_pairs}
    author_vectors = []

    authors = get_user_model().objects.all()
    print(f"👥 Computing author embeddings for {authors.count()} authors...")
    for author in tqdm(authors, desc="👤 Processing authors"):
        authored_blog_ids = list(author.blogs.values_list("id", flat=True))
        vectors = [
            blog_id_to_vec[str(bid)]
            for bid in authored_blog_ids
            if str(bid) in blog_id_to_vec
        ]
        if vectors:
            avg_vector = np.mean(vectors, axis=0).astype(np.float32)
            author_vectors.append((str(author.id), avg_vector.tolist()))

    return author_vectors


def compute_and_save_author_embeddings(blog_emb_pairs):
    author_vectors = compute_author_embeddings(blog_emb_pairs)
    if author_vectors:
        print("⬆️ Uploading author embeddings to Pinecone...")
        author_index = get_pinecone_index(AUTHOR_INDEX_NAME)
        upsert_vectors(author_index, author_vectors)
        print(f"✅ Uploaded embeddings for {len(author_vectors)} authors.")
    else:
        print("⚠️ No author embeddings to upload.")
