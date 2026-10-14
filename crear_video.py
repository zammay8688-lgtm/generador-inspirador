from PIL import Image, ImageFilter
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
src = ROOT / 'imagen-del-dia.png'
poster = ROOT / 'poster-vertical.png'
out = ROOT / 'video-del-dia.mp4'
if not src.exists():
    raise SystemExit('No existe imagen-del-dia.png. Ejecuta primero generar_diario.py')

im = Image.open(src).convert('RGB')
bg = im.resize((1080, 1920), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(24))
overlay = Image.new('RGBA', bg.size, (0, 0, 0, 75))
bg = Image.alpha_composite(bg.convert('RGBA'), overlay)
card = im.resize((960, 960), Image.Resampling.LANCZOS)
bg.alpha_composite(card.convert('RGBA'), ((1080-960)//2, (1920-960)//2))
bg.convert('RGB').save(poster, quality=95)

# Pista ambiental original creada con tonos sintetizados. No usa una canción externa.
filter_complex = (
    "sine=frequency=220:sample_rate=48000:duration=15[a0];"
    "sine=frequency=277.18:sample_rate=48000:duration=15[a1];"
    "sine=frequency=329.63:sample_rate=48000:duration=15[a2];"
    "[a0]volume=0.035[a0v];[a1]volume=0.025[a1v];[a2]volume=0.02[a2v];"
    "[a0v][a1v][a2v]amix=inputs=3:duration=longest,"
    "afade=t=in:st=0:d=2,afade=t=out:st=12:d=3[a]"
)
cmd = [
    'ffmpeg', '-y', '-loop', '1', '-i', str(poster),
    '-f', 'lavfi', '-i', filter_complex,
    '-map', '0:v:0', '-map', '1:a:0',
    '-vf', "scale=4320:-2,zoompan=z='min(zoom+0.00025,1.10)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=450:s=1080x1920:fps=30,format=yuv420p",
    '-t', '15', '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
    '-c:a', 'aac', '-b:a', '128k', '-ar', '48000', '-movflags', '+faststart',
    str(out)
]
subprocess.run(cmd, check=True)
print(f'Video creado: {out.name}')
