from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import json, os, random, textwrap, urllib.parse, urllib.request

ROOT=Path(__file__).parent
TZ=ZoneInfo("America/Mexico_City")
now=datetime.now(TZ)
key=now.strftime("%Y-%m-%d")
frases=json.loads((ROOT/"frases.json").read_text(encoding="utf-8"))
hist_path=ROOT/"historial.json"
hist=json.loads(hist_path.read_text(encoding="utf-8")) if hist_path.exists() else {}
usadas={v["frase"] for v in hist.values() if isinstance(v,dict) and "frase" in v}
disponibles=[f for f in frases if f not in usadas]
if not disponibles:
    usadas=set(); disponibles=frases
frase=random.SystemRandom().choice(disponibles)

W=H=1080
paletas=[("#071952","#35A29F","#FFE17B"),("#3D246C","#F875AA","#FFD6A5"),("#163020","#B6C4B6","#EEF0E5"),("#001C30","#64CCC5","#DAFFFB")]
pal=paletas[len(hist)%len(paletas)]
img=Image.new("RGB",(W,H),pal[0]); d=ImageDraw.Draw(img)
for y in range(H):
    t=y/(H-1); a=tuple(int(pal[0][i:i+2],16) for i in (1,3,5)); b=tuple(int(pal[1][i:i+2],16) for i in (1,3,5))
    c=tuple(int(a[j]*(1-t)+b[j]*t) for j in range(3)); d.line((0,y,W,y),fill=c)
font_candidates=["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"]
font_path=next((p for p in font_candidates if Path(p).exists()),font_candidates[0])
reg_path=font_path.replace("-Bold","")
Fdate=ImageFont.truetype(font_path,42); Fquote=ImageFont.truetype(font_path,58); Fbrand=ImageFont.truetype(font_path,30)
dias=["lunes","martes","miércoles","jueves","viernes","sábado","domingo"]
meses=["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"]
def center(text,y,font,fill):
    box=d.textbbox((0,0),text,font=font); d.text(((W-(box[2]-box[0]))/2,y),text,font=font,fill=fill)
center(dias[now.weekday()].upper(),130,Fdate,pal[2]); center(f"{now.day} de {meses[now.month-1]} de {now.year}",194,Fbrand,"white")
# Ajuste por ancho real
words=frase.split(); lines=[]; line=""
for w in words:
    test=(line+" "+w).strip()
    if d.textbbox((0,0),test,font=Fquote)[2] > 850 and line: lines.append(line); line=w
    else: line=test
if line: lines.append(line)
y=430-(len(lines)-1)*38
for line in lines: center(line,y,Fquote,"white"); y+=78
brand=os.getenv("NOMBRE_PAGINA","Inspira tu día")
center(brand,860,Fbrand,pal[2]); center("Una pausa para recordar lo importante",915,ImageFont.truetype(font_path,22),"white")
out=ROOT/"public"/"imagen-del-dia.png"; img.save(out)
hist[key]={"frase":frase,"archivo":str(out.name)}; hist_path.write_text(json.dumps(hist,ensure_ascii=False,indent=2),encoding="utf-8")

# Publicación opcional en Página de Facebook
page_id=os.getenv("FACEBOOK_PAGE_ID")
token=os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
version=os.getenv("META_GRAPH_VERSION")
if page_id and token and version:
    import requests
    mensaje = f"{dias[now.weekday()].capitalize()}, {now.day} de {meses[now.month-1]} de {now.year}\n\n{frase}"
    with out.open("rb") as image_file:
        response = requests.post(
            f"https://graph.facebook.com/{version}/{page_id}/photos",
            data={"access_token": token, "message": mensaje},
            files={"source": ("imagen-del-dia.png", image_file, "image/png")},
            timeout=60,
        )
    response.raise_for_status()
    print(response.text)
else:
    print("Imagen creada. Publicación omitida porque faltan secretos de Meta.")
