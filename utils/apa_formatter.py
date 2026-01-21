def format_multiple_references(papers):
    refs = []
    for p in papers:
        authors = ", ".join(a["name"] for a in p.get("authors", [])[:3])
        refs.append(
            f"{authors} ({p.get('year','n.d.')}). {p.get('title')}. {p.get('url')}"
        )
    return "\n".join(refs)
