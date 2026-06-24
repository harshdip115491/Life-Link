# =========================
# search_utils.py (CLEAN)
# =========================

def _to_dict(row):
    """
    Converts SQLite Row or dict to standard dictionary
    """
    if hasattr(row, "keys"):
        return dict(row)
    return row


def search(data, query, keys=None):
    """
    Flexible search utility:
    - data: list of rows (sqlite Row or dict)
    - query: search string
    - keys: optional list of fields to search in
    """

    if not query:
        return []

    query = query.lower().strip()
    results = []

    for row in data:
        row_dict = _to_dict(row)

        # decide which fields to search
        search_fields = keys if keys else row_dict.keys()

        for key in search_fields:
            value = str(row_dict.get(key, "")).lower()

            if query in value:
                results.append(row_dict)
                break

    return results


def sort_data(data, key, reverse=False):
    """
    Sort list of dictionaries or sqlite rows by a key
    """

    def get_value(item):
        item_dict = _to_dict(item)
        return item_dict.get(key, "")

    try:
        return sorted(data, key=get_value, reverse=reverse)
    except Exception:
        return data


def filter_data(data, **conditions):
    """
    Advanced filtering:
    Example:
        filter_data(users, status="active", city="Mumbai")
    """

    results = []

    for row in data:
        row_dict = _to_dict(row)

        match = True
        for k, v in conditions.items():
            if str(row_dict.get(k, "")).lower() != str(v).lower():
                match = False
                break

        if match:
            results.append(row_dict)

    return results