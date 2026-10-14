from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json, math, subprocess
from mido import Message, MidiFile, MidiTrack, MetaMessage, bpm2tempo

ROOT=Path(__file__).resolve().parent
DUR=15; FPS=30; W,H=720,1280
hoy=datetime.now(ZoneInfo('America/Mexico_City'))
frases=json.loads((ROOT/'frases-365.json').read_text(encoding='utf-8'))
fondos=sorted((ROOT/'fondos').glob('fondo-*.jpg'))
frase=frases[(hoy.timetuple().tm_yday-1)%len(frases)]
fondo=fondos[(hoy.timetuple().tm_yday-1)%len(fondos)]
dias=['LUNES','MARTES','MIÉRCOLES','JUEVES','VIERNES','SÁBADO','DOMINGO']
meses=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
fecha=f'{hoy.day} de {meses[hoy.month-1]} de {hoy.year}'
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
Fday=ImageFont.truetype(font,40); Fdate=ImageFont.truetype(font,25); Fquote=ImageFont.truetype(font,42); Fbrand=ImageFont.truetype(font,30); Fsmall=ImageFont.truetype(font,18)

def wrap(text,ft,maxw):
 d=ImageDraw.Draw(Image.new('RGB',(1,1))); lines=[]; line=''
 for word in text.split():
  test=(line+' '+word).strip()
  if d.textbbox((0,0),test,font=ft)[2]>maxw and line: lines.append(line); line=word
  else: line=test
 if line: lines.append(line)
 return lines

def ease(x):
 x=max(0,min(1,x)); return x*x*(3-2*x)
def window(t,a,b,fade=.8): return min(ease((t-a)/fade),ease((b-t)/fade))
def centered(d,text,y,ft,fill,alpha=255,xoff=0):
 box=d.textbbox((0,0),text,font=ft); x=(W-(box[2]-box[0]))/2+xoff
 d.text((x+2,y+3),text,font=ft,fill=(0,0,0,int(alpha*.7)))
 d.text((x,y),text,font=ft,fill=(*fill,alpha))

src=Image.open(fondo).convert('RGB')
# Create moving text frame stream and encode silent video.
cmd=['ffmpeg','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-', '-an','-c:v','libx264','-preset','fast','-crf','22','-pix_fmt','yuv420p',str(ROOT/'video-sin-audio.mp4')]
proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
for n in range(DUR*FPS):
 t=n/FPS; zoom=1+0.045*(t/DUR)
 scale=max(W/src.width,H/src.height)*zoom
 im=src.resize((int(src.width*scale),int(src.height*scale)),Image.Resampling.LANCZOS)
 # gentle left-to-right pan
 maxx=max(0,im.width-W); x=int(maxx*(.35+.30*t/DUR)); y=max(0,(im.height-H)//2)
 frame=im.crop((x,y,x+W,y+H)).convert('RGBA')
 frame=Image.alpha_composite(frame,Image.new('RGBA',(W,H),(0,0,0,78)))
 layer=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(layer)
 # Date slides in, then fades out.
 a1=window(t,.3,4.6); slide1=int((1-ease((t-.3)/1.0))*-90)
 centered(d,dias[hoy.weekday()],138,Fday,(255,226,125),int(255*a1),slide1)
 centered(d,fecha,195,Fdate,(255,255,255),int(255*a1),-slide1)
 # Quote fades and rises clearly from seconds 3.7 to 12.7.
 a2=window(t,3.7,12.8,1.1); rise=int((1-ease((t-3.7)/1.2))*85)
 lines=wrap(frase,Fquote,620); start=540-len(lines)*31+rise
 for j,line in enumerate(lines): centered(d,line,start+j*58,Fquote,(255,255,255),int(255*a2))
 # Brand appears at end.
 a3=ease((t-10.7)/1.2)
 centered(d,'POEMA DEL ALMA',1030,Fbrand,(255,226,125),int(255*a3))
 centered(d,'Una pausa para recordar lo importante',1080,Fsmall,(255,255,255),int(230*a3))
 frame=Image.alpha_composite(frame,layer).convert('RGB')
 proc.stdin.write(frame.tobytes())
proc.stdin.close(); proc.wait()
if proc.returncode: raise SystemExit('FFmpeg no pudo crear el video base')

# Create a short original piano melody as MIDI.
mid=MidiFile(ticks_per_beat=480); tr=MidiTrack(); mid.tracks.append(tr)
tr.append(MetaMessage('set_tempo',tempo=bpm2tempo(84),time=0)); tr.append(Message('program_change',program=0,time=0))
melody=[60,64,67,72,69,67,64,62,60,64,67,71,69,65,64,62,60,67,64,60]
beats=.75
for note in melody:
 tr.append(Message('note_on',note=note,velocity=54,time=0))
 tr.append(Message('note_off',note=note,velocity=0,time=int(480*beats)))
mid.save(ROOT/'melodia.mid')

sf_candidates=[Path('/usr/share/sounds/sf2/FluidR3_GM.sf2'),Path('/usr/share/sounds/sf2/TimGM6mb.sf2'),Path('/usr/share/sounds/sf2/default-GM.sf2')]
sf=next((p for p in sf_candidates if p.exists()),None)
if not sf: raise SystemExit('No se encontró el banco de sonido instrumental')
subprocess.run(['fluidsynth','-ni',str(sf),str(ROOT/'melodia.mid'),'-F',str(ROOT/'musica-piano.wav'),'-r','48000'],check=True)
# Merge actual piano audio and upscale to 1080x1920.
subprocess.run(['ffmpeg','-y','-i',str(ROOT/'video-sin-audio.mp4'),'-i',str(ROOT/'musica-piano.wav'),'-filter_complex','[0:v]scale=1080:1920[v];[1:a]afade=t=in:st=0:d=1,afade=t=out:st=12:d=3,volume=0.9[a]','-map','[v]','-map','[a]','-t',str(DUR),'-c:v','libx264','-preset','medium','-crf','23','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-movflags','+faststart',str(ROOT/'video-del-dia.mp4')],check=True)
print('Video con animación visible y piano creado: video-del-dia.mp4')
