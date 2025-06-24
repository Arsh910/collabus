from blog.models import Blogs
from blog.recommender.model.model import load_model, load_device
from blog.recommender.embeddings.blog_embeddings import compute_and_save_blog_embeddings


def get_blog_text_by_id(blog_id):
    blog = Blogs.objects.filter(id=blog_id).first()
    return blog.text if blog else ""


def update_new_blog_embeddings(new_only=True):
    model, tokenizer = load_model()
    device = load_device()
    compute_and_save_blog_embeddings(model, tokenizer, device, new_only=new_only)


def update_all_blog_embeddings(new_only=False):
    model, tokenizer = load_model()
    device = load_device()
    compute_and_save_blog_embeddings(model, tokenizer, device, new_only=new_only)
