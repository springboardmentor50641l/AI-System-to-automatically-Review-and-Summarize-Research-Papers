def format_references(papers):
    refs = []
    for p in papers:
        authors = ", ".join(a["name"] for a in p.get("authors", []))
        refs.append(f"{authors} ({p.get('year')}). {p.get('title')}.")

    return "\n".join(refs)
