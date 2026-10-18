import os, json, textwrap, hashlib
from datetime import datetime, date
from zoneinfo import ZoneInfo
from urllib.request import Request, urlopen
from PIL import Image, ImageDraw, ImageFont

TZ=ZoneInfo('America/Mexico_City')
DAYS=['lunes','martes','miércoles','jueves','viernes','sábado','domingo']
MONTHS=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
OPEN=['Hoy recuerda que','En este nuevo día,','Con el corazón en calma,','Antes de continuar tu camino,','Respira profundo y reconoce que','Que la serenidad te permita comprender que','Aun en los días difíciles,','Cada amanecer nos enseña que','Cuando confías en tu proceso,','Mientras avanzas, no olvides que']
CORE=['los pequeños pasos también construyen grandes destinos','la gratitud transforma la manera de mirar la vida','siempre existe una oportunidad para comenzar de nuevo','tu historia también se escribe con cada intento','la calma puede ser una forma poderosa de avanzar','lo cotidiano guarda momentos extraordinarios','cada etapa tiene un propósito que descubrir','tu ritmo merece respeto y paciencia','la esperanza abre caminos donde antes solo había dudas','el amor se demuestra con presencia y pequeños gestos','la constancia convierte los sueños en caminos posibles','la vida sabe renovarse después de cada tormenta','cada dificultad puede dejar una enseñanza valiosa','confiar en ti también es cuidar tu futuro','la familia se fortalece con escucha y cariño','ningún esfuerzo sincero pasa completamente desapercibido','las mejores transformaciones comienzan desde dentro','un nuevo amanecer puede cambiar la dirección de tu historia','la bondad que compartes siempre deja una huella','también mereces descansar mientras construyes tus sueños']
CLOSE=['y permite que esa verdad acompañe tus pasos','porque avanzar con intención transforma el camino','pues lo sencillo también puede ser maravilloso','y deja espacio para que llegue algo bueno','porque cada día trae una posibilidad diferente','pues volver a intentarlo ya es una victoria','y recuerda agradecer todo lo que ya has construido','porque tu luz también puede inspirar a alguien más','pues vivir el presente es una forma de agradecer','y confía en todo lo que todavía puede florecer']
PALETTES=[('#173f38','#d3a24c','#fff7e7'),('#203b59','#8e718d','#ffffff'),('#174d43','#70a983','#fff9df'),('#422f58','#c57873','#fff4ed'),('#3b402d','#c7aa67','#ffffed'),('#1e4b5b','#67a8a3','#f4ffff'),('#72452c','#d5ae68','#fff8e8'),('#34304f','#8993cf','#fff7ff'),('#384f34','#adb66b','#fbffe9'),('#4d3443','#d793aa','#fff3f8')]

def font(size,bold=False):
 p='/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
 return ImageFont.truetype(p,size)
def content_index(now):
 # 4 franjas diarias: 08, 12, 16 y 20 h. Produce 2,000 piezas antes de repetir.
 slots=[8,12,16,20]; slot=min(range(4),key=lambda i:abs(now.hour-slots[i]))
 return (((now.date()-date(2026,1,1)).days*4)+slot)%2000
def make_quote(i):
 # 10 x 20 x 10 = 2,000 combinaciones exactas.
 a=OPEN[i//200]; b=CORE[(i//10)%20]; c=CLOSE[i%10]
 return f'{a} {b}, {c}.'
def render(now,i,brand):
 quote=make_quote(i); a,b,ink=PALETTES[i%len(PALETTES)]
 im=Image.new('RGB',(1080,1080)); px=im.load()
 for y in range(1080):
  t=y/1079; color=tuple(int(int(a[j+1:j+3],16)*(1-t)+int(b[j+1:j+3],16)*t) for j in (0,2,4))
  for x in range(1080): px[x,y]=color
 d=ImageDraw.Draw(im,'RGBA'); d.rectangle((60,60,1020,1020),fill=(0,0,0,82))
 col=ink; date_text=f'{DAYS[now.weekday()]} {now.day} de {MONTHS[now.month-1]} de {now.year}'.upper()
 d.text((540,165),date_text,font=font(34),fill=col,anchor='mm'); d.rectangle((430,220,650,225),fill=col)
 # Decoración diferente por índice
 for n in range(16):
  x=(n*137+i*29)%1080; y=90+(n%6)*170; r=18+((i+n*7)%42)
  d.ellipse((x-r,y-r,x+r,y+r),outline=col,width=2)
 size=64; lines=textwrap.wrap('“'+quote+'”',width=29)
 while len(lines)>7 and size>40: size-=3; lines=textwrap.wrap('“'+quote+'”',width=31)
 lh=int(size*1.28); y=520-(len(lines)-1)*lh/2
 for line in lines: d.text((540,y),line,font=font(size,True),fill=col,anchor='mm'); y+=lh
 themes=['GRATITUD','ESPERANZA','VIDA','FE','SUPERACIÓN','FAMILIA','NATURALEZA','PROPÓSITO']
 d.text((540,835),themes[i%len(themes)],font=font(27),fill=col,anchor='mm')
 d.text((540,935),brand,font=font(36,True),fill=col,anchor='mm')
 path='reflexion.png'; im.save(path,optimize=True); return path,quote
def publish(path,caption):
 page=os.environ['FB_PAGE_ID']; token=os.environ['FB_PAGE_TOKEN']; ver=os.getenv('FB_API_VERSION','v25.0'); boundary='----Reflexiones2000'; body=b''
 for k,v in [('caption',caption),('access_token',token)]: body+=f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
 body+=f'--{boundary}\r\nContent-Disposition: form-data; name="source"; filename="reflexion.png"\r\nContent-Type: image/png\r\n\r\n'.encode()+open(path,'rb').read()+b'\r\n'+f'--{boundary}--\r\n'.encode()
 req=Request(f'https://graph.facebook.com/{ver}/{page}/photos',data=body,headers={'Content-Type':f'multipart/form-data; boundary={boundary}'})
 with urlopen(req,timeout=60) as r:return json.loads(r.read())
if __name__=='__main__':
 now=datetime.now(TZ); i=int(os.getenv('IMAGE_INDEX',content_index(now)))%2000; brand=os.getenv('BRAND','Poema del Alma')
 path,quote=render(now,i,brand); caption=f'{quote}\n\n#PoemaDelAlma #ReflexiónDelDía #Inspiración'; print(json.dumps({'index':i,'result':publish(path,caption)},ensure_ascii=False))
