import os
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parent
video=ROOT/'video-del-dia.mp4'
texto=(ROOT/'publicacion-del-dia.txt').read_text(encoding='utf-8') if (ROOT/'publicacion-del-dia.txt').exists() else 'Poema del alma | Inspiración del día'
page_id=os.environ['FACEBOOK_PAGE_ID']
token=os.environ['FACEBOOK_PAGE_ACCESS_TOKEN']
version=os.getenv('META_GRAPH_VERSION','v26.0')
if not video.exists(): raise SystemExit('No existe video-del-dia.mp4')
url=f'https://graph.facebook.com/{version}/{page_id}/videos'
with video.open('rb') as f:
    r=requests.post(url,data={'access_token':token,'title':'Inspiración del día','description':texto},files={'source':('video-del-dia.mp4',f,'video/mp4')},timeout=300)
if not r.ok: raise SystemExit(f'Meta devolvió HTTP {r.status_code}: {r.text}')
print('Video enviado a Facebook. ID:',r.json().get('id'))
