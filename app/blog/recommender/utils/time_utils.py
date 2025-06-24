from datetime import datetime


def time_decay_weight(event_time, current_time, is_like=False, half_life_days=7):
    if isinstance(event_time, str):
        event_time = datetime.fromisoformat(event_time)

    time_diff_days = (current_time - event_time).total_seconds() / (3600 * 24)
    decay = 0.5 ** (time_diff_days / half_life_days)

    base_weight = 2.0 if is_like else 1.0
    return base_weight * decay
