def serialize_sets(x):
    if isinstance(x, set):
        return list(x)

    return x
