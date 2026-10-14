from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import array, json, math, subprocess, wave

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'video-del-dia.mp4'
DUR = 15
FPS = 30
W, H = 1080, 1920
TZ = ZoneInfo('America/Mexico_City')
hoy = datetime.now(TZ)

frases = json.loads((ROOT / 'frases-365.json').read_text(encoding='utf-8'))
fondos = sorted((ROOT / 'fondos').glob('fondo-*.jpg'))
frase = frases[(hoy.timetuple().tm_yday - 1) % len(frases)]
fondo = fondos[(hoy.timetuple().tm_yday - 1) % len(fondos)]

dias = ['LUNES','MARTES','MIÉRCOLES','JUEVES','VIERNES','SÁBADO','DOMINGO']
meses = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
fecha = f'{hoy.day} de {meses[hoy.month-1]} de {hoy.year}'

font_bold = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font_reg = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

# Fondo vertical sin texto incrustado
im = Image.open(fondo).convert('RGB')
esc = max(W/im.width, H/im.height)
im = im.resize((int(im.width*esc), int(im.height*esc)), Image.Resampling.LANCZOS)
im = im.crop(((im.width-W)//2, (im.height-H)//2, (im.width+W)//2, (im.height+H)//2))
im = im.filter(ImageFilter.GaussianBlur(1.5))
im = Image.alpha_composite(im.convert('RGBA'), Image.new('RGBA',(W,H),(0,0,0,82)))
im.convert('RGB').save(ROOT/'video-fondo.jpg', quality=94)

def center_text_layer(lines, sizes, ys, colors, path):
    layer = Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(layer)
    for text,size,y,color in zip(lines,sizes,ys,colors):
        font=ImageFont.truetype(font_bold if size>=34 else font_reg,size)
        box=d.textbbox((0,0),text,font=font); x=(W-(box[2]-box[0]))/2
        d.text((x+3,y+4),text,font=font,fill=(0,0,0,155))
        d.text((x,y),text,font=font,fill=color)
    layer.save(path)

def wrap(text, font, maxw):
    d=ImageDraw.Draw(Image.new('RGB',(1,1))); lines=[]; line=''
    for word in text.split():
        test=(line+' '+word).strip()
        if d.textbbox((0,0),test,font=font)[2] > maxw and line:
            lines.append(line); line=word
        else: line=test
    if line: lines.append(line)
    return lines

center_text_layer([dias[hoy.weekday()],fecha],[54,34],[220,300],[(255,225,123,255),(255,255,255,255)],ROOT/'capa-fecha.png')
qfont=ImageFont.truetype(font_bold,58); qlines=wrap(frase,qfont,900)
qys=[]; start=H//2-(len(qlines)*76)//2
for n in range(len(qlines)): qys.append(start+n*76)
center_text_layer(qlines,[58]*len(qlines),qys,[(255,255,255,255)]*len(qlines),ROOT/'capa-frase.png')
center_text_layer(['POEMA DEL ALMA','Una pausa para recordar lo importante'],[40,25],[1540,1610],[(255,225,123,255),(255,255,255,235)],ROOT/'capa-firma.png')

# Música original tipo arpegio ambiental, creada matemáticamente
sr=48000; samples=array.array('h'); total=sr*DUR
notes={'C4':261.63,'E4':329.63,'G4':392.00,'A3':220.00,'C4b':261.63,'E4b':329.63,'F3':174.61,'A3b':220.00,'C4c':261.63,'G3':196.00,'B3':246.94,'D4':293.66}
pattern=[261.63,329.63,392.00,329.63,220.00,261.63,329.63,261.63,174.61,220.00,261.63,220.00,196.00,246.94,293.66,246.94]
step=.75
for n in range(total):
    t=n/sr; idx=int(t/step)%len(pattern); local=t%step; f=pattern[idx]
    attack=min(1,local/.08); release=max(0,min(1,(step-local)/.20)); env=attack*release
    # sonido suave tipo campana/piano con armónicos y pad grave
    tone=(math.sin(2*math.pi*f*t)+0.38*math.sin(2*math.pi*2*f*t)+0.16*math.sin(2*math.pi*3*f*t))*env
    pad=0.22*math.sin(2*math.pi*(f/2)*t)
    global_env=min(1,t/1.2)*min(1,(DUR-t)/2.2)
    val=int(max(-1,min(1,(0.22*tone+0.10*pad)*global_env))*32767)
    samples.append(val); samples.append(val)
with wave.open(str(ROOT/'musica-original.wav'),'wb') as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes(samples.tobytes())

# Capas de texto: fecha aparece y desaparece; frase aparece después; firma al final.
fc=(
"[0:v]scale=1080:1920,format=yuv420p[bg];"
"[1:v]format=rgba,fade=t=in:st=0.4:d=1:alpha=1,fade=t=out:st=3.8:d=1:alpha=1[date];"
"[2:v]format=rgba,fade=t=in:st=3.5:d=1.3:alpha=1,fade=t=out:st=11.5:d=1.2:alpha=1[quote];"
"[3:v]format=rgba,fade=t=in:st=10.5:d=1.2:alpha=1[sign];"
"[bg][date]overlay=0:0:eof_action=pass[v1];[v1][quote]overlay=0:0:eof_action=pass[v2];[v2][sign]overlay=0:0:format=auto[v]"
)
cmd=['ffmpeg','-y','-loop','1','-t',str(DUR),'-i',str(ROOT/'video-fondo.jpg'),
     '-loop','1','-t',str(DUR),'-i',str(ROOT/'capa-fecha.png'),
     '-loop','1','-t',str(DUR),'-i',str(ROOT/'capa-frase.png'),
     '-loop','1','-t',str(DUR),'-i',str(ROOT/'capa-firma.png'),
     '-i',str(ROOT/'musica-original.wav'),'-filter_complex',fc,'-map','[v]','-map','4:a:0',
     '-t',str(DUR),'-c:v','libx264','-preset','medium','-crf','23','-pix_fmt','yuv420p',
     '-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-movflags','+faststart',str(OUT)]
subprocess.run(cmd,check=True)
print('Video animado con música creado:',OUT.name)
