from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, is_naive
from datetime import datetime


def filter_new_relevant_blogs(
    blog_queryset, last_visit_time, top_k, retrieved_ids_ranked
):

    if not last_visit_time:
        # last_time = timezone.now() - timezone.timedelta(days=3)
        last_visit_time = "2025-06-21T3:15:00"
    if isinstance(last_visit_time, str):
        last_time = parse_datetime(last_visit_time)
    elif isinstance(last_visit_time, datetime):
        last_time = last_visit_time
    else:
        raise ValueError("last_visit_time must be a datetime or ISO 8601 string")

    # Make sure `last_time` is timezone-aware
    if is_naive(last_time):
        last_time = make_aware(last_time)

    # Also make sure blog.date is timezone-aware during comparison
    new_blogs = [
        b
        for b in blog_queryset
        if b.date and not is_naive(b.date) and b.date > last_time
    ]
    old_blogs = [
        b
        for b in blog_queryset
        if b.date and not is_naive(b.date) and b.date <= last_time
    ]

    id_to_rank = {str(bid): rank for rank, bid in enumerate(retrieved_ids_ranked)}
    new_blogs.sort(key=lambda b: id_to_rank.get(str(b.id), float("inf")))
    old_blogs.sort(key=lambda b: id_to_rank.get(str(b.id), float("inf")))

    n_new = min(int(0.7 * top_k), len(new_blogs))
    n_old = top_k - n_new

    selected_ids = [b.id for b in new_blogs[:n_new]] + [b.id for b in old_blogs[:n_old]]
    return selected_ids
