from blog.models import Blogs
from blog.recommender.utils.recommend_utils import filter_new_relevant_blogs
from blog.recommender.utils.pincone_utils import get_pinecone_index
import numpy as np


def recommend(user_id, last_visit_time, top_k=20):
    user_id = str(user_id)

    blog_index = get_pinecone_index("blog-embeddings")
    user_index = get_pinecone_index("user-embeddings")
    user_vector_response = user_index.fetch([user_id])
    if user_id not in user_vector_response.vectors:
        return {"recommended_blogs": [], "recommended_authors": []}

    user_vector = np.array(
        user_vector_response.vectors[user_id].values, dtype=np.float32
    ).reshape(1, -1)

    blog_results = blog_index.query(
        vector=user_vector.tolist()[0], top_k=top_k * 5, include_values=False
    )
    retrieved_blog_ids = [match.id for match in blog_results.matches]
    retrieved_blogs = Blogs.objects.filter(id__in=retrieved_blog_ids)
    filtered_blog_ids = filter_new_relevant_blogs(
        retrieved_blogs, last_visit_time, top_k, retrieved_blog_ids
    )

    recommended_blogs = Blogs.objects.filter(id__in=filtered_blog_ids)
    recommended_data = [
        {
            "id": blog.id,
            "timestamp": blog.date.isoformat(),
        }
        for blog in recommended_blogs
    ]
    return {"recommended_blogs": recommended_data}


def recommend_authors(user_id, top_k=20):
    user_id = str(user_id)
    if top_k is None or not isinstance(top_k, int) or top_k <= 0:
        top_k = 20

    author_index = get_pinecone_index("author-embeddings")
    user_index = get_pinecone_index("user-embeddings")

    user_vector_response = user_index.fetch([user_id])
    if user_id not in user_vector_response.vectors:
        return {"recommended_authors": []}

    user_vector_values = user_vector_response.vectors[user_id].values
    if user_vector_values is None or any(v is None for v in user_vector_values):
        return {"recommended_authors": []}

    user_vector = np.array(user_vector_values, dtype=np.float32).reshape(1, -1)
    author_results = author_index.query(
        vector=user_vector.tolist()[0], top_k=top_k, include_values=False
    )

    recommended_author_ids = [
        match.id for match in author_results.matches if match and match.id is not None
    ]

    return {"recommended_authors": recommended_author_ids}
