def merge_dicts(a, b):
    """Copy values from B into A. destructively modifies A."""
    def rec(a, b):
        for k in b.keys():
            new = b[k]
            if isinstance(new, dict):
                existing = a.get(k, a)
                if existing is a:
                    a[k] = new
                else:
                    if isinstance(existing, dict):
                        rec(existing, new)
                    else:
                        a[k] = new
            else:
                a[k] = new

    rec(a, b)

    return a
