import numpy as np
from datetime import datetime
from tqdm import tqdm

from blog.recommender.logs.mongo import (
    get_user_read_logs,
    get_user_like_logs,
    get_latest_interaction_timestamp,
    mark_user_as_uploaded,
    fetch_existing_user_ids,
    get_user_last_upload_time,
)
from blog.recommender.utils.time_utils import time_decay_weight
from blog.recommender.utils.pincone_utils import (
    get_pinecone_index,
    upsert_vectors,
    fetch_vectors_by_ids,
)

USER_INDEX_NAME = "user-embeddings"
BLOG_INDEX_NAME = "blog-embeddings"


def compute_user_embedding(user_id, device):
    now = datetime.utcnow()

    read_logs = get_user_read_logs(user_id)
    like_logs = get_user_like_logs(user_id)

    blog_weights = {}

    for log in like_logs:
        blog_id = str(log["blog_id"])
        weight = time_decay_weight(log["timestamp"], now, is_like=True)
        blog_weights[blog_id] = blog_weights.get(blog_id, 0) + weight

    for log in read_logs:
        blog_id = str(log["blog_id"])
        weight = time_decay_weight(log["timestamp"], now, is_like=False)
        blog_weights[blog_id] = blog_weights.get(blog_id, 0) + weight

    if not blog_weights:
        print(f"⚠️ No valid interaction logs for user {user_id}")
        return None

    blog_ids = list(blog_weights.keys())

    print(
        f"📡 Fetching {len(blog_ids)} blog embeddings from Pinecone for user {user_id}"
    )
    blog_index = get_pinecone_index(BLOG_INDEX_NAME)
    blog_vectors = fetch_vectors_by_ids(blog_index, blog_ids)

    if not blog_vectors:
        print(f"⚠️ No embeddings found for blogs read/liked by user {user_id}")
        return None

    vectors = []
    weights = []

    for blog_id, vector in blog_vectors.items():
        if hasattr(vector, "values"):
            vec = np.array(vector.values, dtype=np.float32)
        else:
            vec = np.array(vector, dtype=np.float32)
        vectors.append(vec)
        weights.append(blog_weights[blog_id])

    try:
        user_embedding = np.average(vectors, axis=0, weights=weights).astype(np.float32)
        return user_embedding
    except Exception as e:
        print(f"❌ Error computing user embedding for {user_id}: {e}")
        return None


def compute_and_save_user_embeddings(
    model, tokenizer, device, reads_collection, likes_collection, new_only=False
):
    print("\n📋 Gathering unique user IDs from logs...")
    all_user_ids = set(
        reads_collection.distinct("user_id") + likes_collection.distinct("user_id")
    )

    if new_only:
        known_ids = fetch_existing_user_ids()
        user_ids = []

        print("🔍 Filtering for new or updated users...")
        for user_id in tqdm(all_user_ids, desc="📅 Checking timestamps", unit="user"):
            latest_interaction = get_latest_interaction_timestamp(user_id)
            last_upload = get_user_last_upload_time(user_id)

            if latest_interaction is None:
                continue

            if str(user_id) not in known_ids or (
                last_upload and latest_interaction > last_upload
            ):
                user_ids.append(user_id)

        print(f"🆕 Found {len(user_ids)} new or updated users to embed.")
    else:
        user_ids = list(all_user_ids)
        print(f"🔄 Full refresh: {len(user_ids)} users to embed.")

    if not user_ids:
        print("⚠️ No users to embed.\n")
        return

    print("\n⚙️ Computing user embeddings...")
    vectors = []
    for user_id in tqdm(user_ids, desc="🧠 Embedding users", unit="user"):
        emb = compute_user_embedding(user_id, device)
        if emb is not None:
            vectors.append((str(user_id), emb.tolist()))

    if vectors:
        print("\n⬆️ Uploading user embeddings to Pinecone...")
        pinecone_index = get_pinecone_index(USER_INDEX_NAME)
        upsert_vectors(pinecone_index, vectors)
        print(f"✅ Uploaded {len(vectors)} user embeddings to Pinecone.")

        print("\n🗂️ Saving user embedding logs to MongoDB...")
        for user_id, _ in tqdm(vectors, desc="📝 Logging uploads", unit="user"):
            mark_user_as_uploaded(user_id)
        print("✅ Saved user embedding logs.\n")
    else:
        print("⚠️ No user embeddings to upload.\n")
