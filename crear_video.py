from PIL import Image, ImageFilter
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
src = ROOT / "imagen-del-dia.png"
poster = ROOT / "poster-vertical.png"
out = ROOT / "video-del-dia.mp4"

if not src.exists():
    raise SystemExit("No existe imagen-del-dia.png. Ejecuta primero generar_diario.py")

im = Image.open(src).convert("RGB")
bg = im.resize((1080, 1920), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(24))
overlay = Image.new("RGBA", bg.size, (0, 0, 0, 75))
bg = Image.alpha_composite(bg.convert("RGBA"), overlay)
card = im.resize((960, 960), Image.Resampling.LANCZOS)
bg.alpha_composite(card.convert("RGBA"), ((1080 - 960) // 2, (1920 - 960) // 2))
bg.convert("RGB").save(poster, quality=95)

# Audio ambiental original sintetizado. No usa canciones externas.
audio = (
    "aevalsrc="
    "0.025*sin(2*PI*220*t)+"
    "0.018*sin(2*PI*277.18*t)+"
    "0.014*sin(2*PI*329.63*t)"
    ":s=48000:d=15"
)

cmd = [
    "ffmpeg", "-y",
    "-loop", "1", "-i", str(poster),
    "-f", "lavfi", "-i", audio,
    "-map", "0:v:0", "-map", "1:a:0",
    "-vf", "scale=2160:-2,zoompan=z='min(zoom+0.00025,1.10)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=450:s=1080x1920:fps=30,format=yuv420p",
    "-af", "afade=t=in:st=0:d=2,afade=t=out:st=12:d=3",
    "-t", "15",
    "-c:v", "libx264", "-preset", "medium", "-crf", "23",
    "-c:a", "aac", "-b:a", "128k", "-ar", "48000",
    "-movflags", "+faststart",
    str(out),
]
subprocess.run(cmd, check=True)
print(f"Video creado: {out.name}")
