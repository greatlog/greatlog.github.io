from scholarly import scholarly
import jsonpickle
import json
from datetime import datetime
from urllib.parse import unquote
import re
import os


def resolve_scholar_id() -> str:
    scholar_id = os.getenv("GOOGLE_SCHOLAR_ID", "").strip()
    if scholar_id:
        return scholar_id

    scholar_url = os.getenv("GOOGLE_SCHOLAR_URL", "").strip()
    if scholar_url:
        match = re.search(r"[?&]user=([^&]+)", scholar_url)
        if match:
            return unquote(match.group(1))

    raise RuntimeError(
        "Google Scholar ID is missing. Set GOOGLE_SCHOLAR_ID or GOOGLE_SCHOLAR_URL."
    )


def main() -> None:
    scholar_id = resolve_scholar_id()
    try:
        author: dict = scholarly.search_author_id(scholar_id)
        scholarly.fill(author, sections=["basics", "indices", "counts", "publications"])
    except Exception as exc:
        raise RuntimeError(
            "Failed to get citation number from Google Scholar. "
            "This can happen when Scholar blocks/rate-limits crawler requests."
        ) from exc

    author["updated"] = str(datetime.now())
    author["publications"] = {v["author_pub_id"]: v for v in author["publications"]}
    print(json.dumps(author, indent=2))

    os.makedirs("results", exist_ok=True)
    with open("results/gs_data.json", "w", encoding="utf-8") as outfile:
        json.dump(author, outfile, ensure_ascii=False)

    shieldio_data = {
        "schemaVersion": 1,
        "label": "citations",
        "message": f"{author.get('citedby', 0)}",
    }
    with open("results/gs_data_shieldsio.json", "w", encoding="utf-8") as outfile:
        json.dump(shieldio_data, outfile, ensure_ascii=False)


if __name__ == "__main__":
    main()
