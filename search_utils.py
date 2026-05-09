def search(data, query):
    return [d for d in data if query.lower() in str(d).lower()]

def sort_data(data, index):
    return sorted(data, key=lambda x: x[index])