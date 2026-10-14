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
bg = Image.alpha_composite(bg.convert("RGBA"), Image.new("RGBA", bg.size, (0, 0, 0, 75)))
card = im.resize((960, 960), Image.Resampling.LANCZOS)
bg.alpha_composite(card.convert("RGBA"), (60, 480))
bg.convert("RGB").save(poster, quality=95)

# Melodia ambiental sintetizada, original y claramente audible.
# Dos acordes suaves alternan durante 15 segundos.
left = (
    "0.10*sin(2*PI*(if(lt(mod(t,8),4),261.63,220.00))*t)+"
    "0.07*sin(2*PI*(if(lt(mod(t,8),4),329.63,277.18))*t)+"
    "0.05*sin(2*PI*(if(lt(mod(t,8),4),392.00,329.63))*t)"
)
right = (
    "0.09*sin(2*PI*(if(lt(mod(t,8),4),261.63,220.00))*t)+"
    "0.08*sin(2*PI*(if(lt(mod(t,8),4),329.63,277.18))*t)+"
    "0.05*sin(2*PI*(if(lt(mod(t,8),4),392.00,329.63))*t)"
)
audio = f"aevalsrc='{left}|{right}':c=stereo:s=48000:d=15"

cmd = [
    "ffmpeg", "-y",
    "-loop", "1", "-i", str(poster),
    "-f", "lavfi", "-i", audio,
    "-map", "0:v:0", "-map", "1:a:0",
    "-vf", "scale=2160:-2,zoompan=z='min(zoom+0.00025,1.10)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=450:s=1080x1920:fps=30,format=yuv420p",
    "-af", "lowpass=f=1600,afade=t=in:st=0:d=1.5,afade=t=out:st=12:d=3,volume=1.6",
    "-t", "15",
    "-c:v", "libx264", "-preset", "medium", "-crf", "23",
    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
    "-movflags", "+faststart",
    str(out),
]
subprocess.run(cmd, check=True)
print(f"Video creado con audio: {out.name}")
