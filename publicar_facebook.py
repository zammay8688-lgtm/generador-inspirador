import os
from pathlib import Path
import requests

page_id = os.environ["FACEBOOK_PAGE_ID"]
token = os.environ["FACEBOOK_PAGE_ACCESS_TOKEN"]
version = os.getenv("META_GRAPH_VERSION", "v26.0")
root = Path(__file__).resolve().parent
image = root / "imagen-del-dia.png"
caption = (root / "publicacion-del-dia.txt").read_text(encoding="utf-8")

if not image.exists():
    raise SystemExit("No existe imagen-del-dia.png")

url = f"https://graph.facebook.com/{version}/{page_id}/photos"
with image.open("rb") as f:
    response = requests.post(
        url,
        data={"message": caption, "access_token": token},
        files={"source": (image.name, f, "image/png")},
        timeout=90,
    )
if not response.ok:
    raise SystemExit(f"Meta devolvió HTTP {response.status_code}: {response.text}")
print("Publicación creada correctamente:", response.json().get("post_id") or response.json().get("id"))
