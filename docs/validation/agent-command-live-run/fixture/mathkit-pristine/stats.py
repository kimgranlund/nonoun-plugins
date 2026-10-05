"""Small statistics helpers."""


def mean(values):
    """Arithmetic mean. Raises ValueError for an empty sequence."""
    values = list(values)
    if not values:
        raise ValueError("mean of empty sequence")
    return sum(values) / len(values)
