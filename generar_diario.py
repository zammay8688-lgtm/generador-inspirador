from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
TZ = ZoneInfo("America/Mexico_City")
hoy = datetime.now(TZ)
frases = json.loads((ROOT / "frases-365.json").read_text(encoding="utf-8"))
fondos = sorted((ROOT / "fondos").glob("fondo-*.jpg"))
if not frases or not fondos:
    raise SystemExit("Faltan frases-365.json o imágenes dentro de fondos/")

dia_anio = hoy.timetuple().tm_yday
frase = frases[(dia_anio - 1) % len(frases)]
fondo = fondos[(dia_anio - 1) % len(fondos)]

W = H = 1080
base = Image.open(fondo).convert("RGB")
escala = max(W / base.width, H / base.height)
nw, nh = int(base.width * escala), int(base.height * escala)
base = base.resize((nw, nh), Image.Resampling.LANCZOS)
img = base.crop(((nw-W)//2, (nh-H)//2, (nw+W)//2, (nh+H)//2))
oscuro = Image.new("RGBA", (W,H), (0,0,0,112))
img = Image.alpha_composite(img.convert("RGBA"), oscuro).convert("RGB")
d = ImageDraw.Draw(img)
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
fecha_font = ImageFont.truetype(font_path, 42)
frase_font = ImageFont.truetype(font_path, 58)
firma_font = ImageFont.truetype(font_path, 29)
dias = ["LUNES","MARTES","MIÉRCOLES","JUEVES","VIERNES","SÁBADO","DOMINGO"]
meses = ["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"]

def centro(texto, y, font, color="white"):
    box=d.textbbox((0,0),texto,font=font)
    d.text(((W-(box[2]-box[0]))/2,y),texto,font=font,fill=color)

def envolver(texto, max_ancho):
    lineas=[]; linea=""
    for palabra in texto.split():
        prueba=(linea+" "+palabra).strip()
        if d.textbbox((0,0),prueba,font=frase_font)[2] > max_ancho and linea:
            lineas.append(linea); linea=palabra
        else: linea=prueba
    if linea: lineas.append(linea)
    return lineas

d.rectangle((62,62,1018,1018), outline=(255,255,255,150), width=2)
centro(dias[hoy.weekday()], 150, fecha_font, "#FFE17B")
centro(f"{hoy.day} de {meses[hoy.month-1]} de {hoy.year}", 215, firma_font)
lineas=envolver(frase, 820)
y=500-(len(lineas)-1)*39
for linea in lineas:
    centro(linea,y,frase_font); y+=78
d.rectangle((440,805,640,809), fill="#FFE17B")
centro("Inspira tu día", 865, firma_font)
centro("Una pausa para recordar lo importante", 925, ImageFont.truetype(font_path,21))
img.save(ROOT / "imagen-del-dia.png", quality=95)
(ROOT / "publicacion-del-dia.txt").write_text(
    f"{dias[hoy.weekday()].capitalize()}, {hoy.day} de {meses[hoy.month-1]} de {hoy.year}\n\n{frase}\n",
    encoding="utf-8"
)
print(f"Creada imagen-del-dia.png con fondo {fondo.name}")
