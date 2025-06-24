from celery import shared_task


@shared_task
def compute_blog_all_embedding_task():
    from blog.recommender.utils.blog_utils import update_all_blog_embeddings

    update_all_blog_embeddings()
    return "Done"


@shared_task
def compute_blog_embedding_task():
    from blog.recommender.utils.blog_utils import update_new_blog_embeddings

    update_new_blog_embeddings()
    return "Done"


@shared_task
def compute_user_all_embedding_task():
    from blog.recommender.utils.user_utils import update_all_user_embeddings

    update_all_user_embeddings()
    return "Done"


@shared_task
def compute_user_embedding_task():
    from blog.recommender.utils.user_utils import update_user_embeddings

    update_user_embeddings()
    return "Done"
