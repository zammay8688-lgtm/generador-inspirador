import json
import os

from datetime import date, datetime
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont


TZ = ZoneInfo("America/Mexico_City")

DAYS = [
    "lunes", "martes", "miércoles", "jueves",
    "viernes", "sábado", "domingo",
]

MONTHS = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre",
    "diciembre",
]

OPEN = [
    "Hoy recuerda que",
    "En este nuevo día,",
    "Con el corazón en calma,",
    "Antes de continuar tu camino,",
    "Respira profundo y reconoce que",
    "Que la serenidad te permita comprender que",
    "Aun en los días difíciles,",
    "Cada amanecer nos enseña que",
    "Cuando confías en tu proceso,",
    "Mientras avanzas, no olvides que",
]

CORE = [
    "los pequeños pasos también construyen grandes destinos",
    "la gratitud transforma la manera de mirar la vida",
    "siempre existe una oportunidad para comenzar de nuevo",
    "tu historia también se escribe con cada intento",
    "la calma puede ser una forma poderosa de avanzar",
    "lo cotidiano guarda momentos extraordinarios",
    "cada etapa tiene un propósito que descubrir",
    "tu ritmo merece respeto y paciencia",
    "la esperanza abre caminos donde antes solo había dudas",
    "el amor se demuestra con presencia y pequeños gestos",
    "la constancia convierte los sueños en caminos posibles",
    "la vida sabe renovarse después de cada tormenta",
    "cada dificultad puede dejar una enseñanza valiosa",
    "confiar en ti también es cuidar tu futuro",
    "la familia se fortalece con escucha y cariño",
    "ningún esfuerzo sincero pasa completamente desapercibido",
    "las mejores transformaciones comienzan desde dentro",
    "un nuevo amanecer puede cambiar la dirección de tu historia",
    "la bondad que compartes siempre deja una huella",
    "también mereces descansar mientras construyes tus sueños",
]

CLOSE = [
    "y permite que esa verdad acompañe tus pasos",
    "porque avanzar con intención transforma el camino",
    "pues lo sencillo también puede ser maravilloso",
    "y deja espacio para que llegue algo bueno",
    "porque cada día trae una posibilidad diferente",
    "pues volver a intentarlo ya es una victoria",
    "y recuerda agradecer todo lo que ya has construido",
    "porque tu luz también puede inspirar a alguien más",
    "pues vivir el presente es una forma de agradecer",
    "y confía en todo lo que todavía puede florecer",
]

PALETTES = [
    ("#173f38", "#d3a24c", "#fff7e7"),
    ("#172844", "#596b9c", "#ffffff"),
    ("#356f56", "#9ecb78", "#fff9df"),
    ("#4e3153", "#df856b", "#fff4ed"),
    ("#183c2d", "#5f8b55", "#ffffed"),
    ("#4c7890", "#a8d2e2", "#f4ffff"),
    ("#263449", "#65778d", "#edfaff"),
    ("#214b60", "#79b7c5", "#f3ffff"),
    ("#72452c", "#d5ae68", "#fff8e8"),
    ("#34304f", "#8993cf", "#fff7ff"),
]

THEMES = [
    "GRATITUD", "ESPERANZA", "VIDA", "FE",
    "SUPERACIÓN", "FAMILIA", "NATURALEZA", "PROPÓSITO",
]


def font(size, bold=False):
    filename = "DejaVuSerif-Bold.ttf" if bold else "DejaVuSerif.ttf"
    path = f"/usr/share/fonts/truetype/dejavu/{filename}"
    return ImageFont.truetype(path, size)


def hex_to_rgb(color):
    return tuple(int(color[pos:pos + 2], 16) for pos in (1, 3, 5))


def content_index(now):
    publication_hours = [0, 3, 6, 9, 12, 15, 18, 21]
    slot = min(
        range(len(publication_hours)),
        key=lambda item: abs(now.hour - publication_hours[item]),
    )
    elapsed_days = (now.date() - date(2026, 1, 1)).days
    return ((elapsed_days * 8) + slot) % 2000


def make_quote(index):
    normalized = index % 2000
    opening = OPEN[normalized // 200]
    core = CORE[(normalized // 10) % 20]
    closing = CLOSE[normalized % 10]
    return f"{opening} {core}, {closing}."


def wrap_text_by_width(drawing, text, selected_font, maximum_width):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        candidate = f"{current_line} {word}".strip()
        box = drawing.textbbox((0, 0), candidate, font=selected_font)
        candidate_width = box[2] - box[0]

        if candidate_width <= maximum_width or not current_line:
            current_line = candidate
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


def draw_mountains(drawing):
    drawing.ellipse((420, 225, 660, 465), fill=(255, 205, 115, 210))
    drawing.polygon([(60, 690), (250, 390), (430, 690)], fill=(92, 105, 126, 235))
    drawing.polygon([(250, 690), (510, 300), (780, 690)], fill=(62, 78, 105, 245))
    drawing.polygon([(590, 690), (830, 410), (1020, 690)], fill=(80, 95, 116, 235))
    drawing.polygon(
        [(440, 405), (510, 300), (590, 420), (548, 398), (510, 440), (478, 397)],
        fill=(245, 245, 248, 230),
    )
    drawing.rectangle((60, 690, 1020, 1020), fill=(42, 78, 62, 175))


def draw_starry_night(drawing, index):
    drawing.ellipse((735, 160, 915, 340), fill=(255, 245, 201, 235))
    drawing.ellipse((780, 135, 950, 305), fill=(25, 39, 70, 255))
    for star in range(60):
        x = (star * 173 + index * 47) % 940 + 70
        y = (star * 97 + index * 29) % 520 + 90
        radius = 2 + (star + index) % 4
        drawing.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(255, 255, 225, 210))
    drawing.polygon([(60, 760), (300, 560), (520, 760)], fill=(29, 48, 69, 235))
    drawing.polygon([(420, 760), (720, 520), (1020, 760)], fill=(20, 39, 60, 245))
    drawing.rectangle((60, 760, 1020, 1020), fill=(16, 34, 53, 220))


def draw_flower_field(drawing, index):
    drawing.ellipse((-180, 590, 720, 1160), fill=(80, 133, 92, 235))
    drawing.ellipse((360, 610, 1270, 1160), fill=(56, 112, 79, 240))
    colors = [(255, 228, 100, 245), (255, 170, 183, 245), (225, 205, 255, 245), (255, 250, 235, 245)]
    for flower in range(48):
        x = (flower * 139 + index * 31) % 900 + 90
        y = (flower * 73) % 270 + 700
        color = colors[flower % len(colors)]
        drawing.line((x, y, x, y + 42), fill=(38, 91, 54, 235), width=4)
        drawing.ellipse((x - 10, y - 10, x + 10, y + 10), fill=color)
        drawing.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(255, 190, 60, 255))


def draw_sea_sunset(drawing):
    drawing.ellipse((425, 225, 655, 455), fill=(255, 193, 90, 230))
    drawing.rectangle((60, 635, 1020, 1020), fill=(36, 105, 135, 195))
    drawing.line((60, 650, 1020, 650), fill=(255, 238, 200, 210), width=5)
    for wave in range(9):
        y = 680 + wave * 38
        for x in (60, 350, 690):
            drawing.arc((x, y, x + 330, y + 65), 190, 350, fill=(230, 246, 255, 185), width=5)
    for reflection in range(8):
        y = 475 + reflection * 25
        half = 100 - reflection * 8
        drawing.line((540 - half, y, 540 + half, y), fill=(255, 224, 150, 150), width=5)


def draw_forest_path(drawing):
    drawing.rectangle((60, 560, 1020, 1020), fill=(35, 82, 54, 215))
    drawing.polygon([(430, 1020), (650, 1020), (585, 650), (505, 650)], fill=(219, 190, 143, 210))
    for tree in range(9):
        x = 70 + tree * 115
        drawing.rectangle((x, 470, x + 34, 940), fill=(78, 52, 38, 240))
        drawing.ellipse((x - 75, 315, x + 110, 610), fill=(31, 91, 59, 240))
        drawing.ellipse((x - 45, 260, x + 80, 490), fill=(45, 111, 68, 225))


def draw_hills_and_clouds(drawing):
    for cloud_x, cloud_y in [(130, 220), (500, 285), (790, 185)]:
        drawing.ellipse((cloud_x, cloud_y, cloud_x + 180, cloud_y + 80), fill=(255, 255, 255, 180))
        drawing.ellipse((cloud_x + 45, cloud_y - 40, cloud_x + 140, cloud_y + 65), fill=(255, 255, 255, 195))
    drawing.ellipse((-230, 600, 710, 1220), fill=(95, 145, 95, 225))
    drawing.ellipse((300, 575, 1270, 1220), fill=(64, 122, 85, 235))
    drawing.ellipse((40, 760, 1100, 1300), fill=(48, 102, 70, 230))


def draw_luminous_rain(drawing, index):
    for drop in range(65):
        x = (drop * 127 + index * 41) % 940 + 70
        y = (drop * 83 + index * 23) % 820 + 90
        length = 25 + (drop % 4) * 10
        drawing.line((x, y, x - 12, y + length), fill=(220, 245, 255, 160), width=3)
    drawing.rectangle((60, 770, 1020, 1020), fill=(28, 61, 82, 170))
    for puddle in range(6):
        center_x = 170 + puddle * 145
        drawing.ellipse((center_x - 75, 860, center_x + 75, 900), outline=(220, 245, 255, 145), width=4)


def draw_reflective_lake(drawing):
    drawing.polygon([(60, 610), (270, 350), (440, 610)], fill=(68, 90, 108, 235))
    drawing.polygon([(340, 610), (565, 320), (780, 610)], fill=(48, 72, 96, 245))
    drawing.polygon([(650, 610), (850, 390), (1020, 610)], fill=(72, 92, 107, 235))
    drawing.rectangle((60, 610, 1020, 1020), fill=(52, 104, 128, 205))
    for reflection in range(13):
        y = 650 + reflection * 28
        half_width = max(65, 235 - reflection * 13)
        drawing.line((540 - half_width, y, 540 + half_width, y), fill=(235, 245, 245, 115), width=4)


def draw_scene(drawing, scene_index, index):
    handlers = [
        lambda: draw_mountains(drawing),
        lambda: draw_starry_night(drawing, index),
        lambda: draw_flower_field(drawing, index),
        lambda: draw_sea_sunset(drawing),
        lambda: draw_forest_path(drawing),
        lambda: draw_hills_and_clouds(drawing),
        lambda: draw_luminous_rain(drawing, index),
        lambda: draw_reflective_lake(drawing),
    ]
    handlers[scene_index % len(handlers)]()


def render(now, index, brand):
    quote = make_quote(index)
    first_color, second_color, text_color = PALETTES[index % len(PALETTES)]
    start_rgb = hex_to_rgb(first_color)
    end_rgb = hex_to_rgb(second_color)

    image = Image.new("RGB", (1080, 1080))
    drawing = ImageDraw.Draw(image, "RGBA")

    # Degradado eficiente, dibujado por filas.
    for y in range(1080):
        transition = y / 1079
        color = tuple(
            int(start_rgb[channel] * (1 - transition) + end_rgb[channel] * transition)
            for channel in range(3)
        )
        drawing.line((0, y, 1080, y), fill=color, width=1)

    scene_index = index % 8
    draw_scene(drawing, scene_index, index)

    # Panel translúcido para mantener legible la reflexión sobre el paisaje.
    drawing.rounded_rectangle(
        (70, 70, 1010, 1010),
        radius=28,
        fill=(0, 0, 0, 108),
        outline=(255, 255, 255, 65),
        width=2,
    )

    date_text = (
        f"{DAYS[now.weekday()]} {now.day} de "
        f"{MONTHS[now.month - 1]} de {now.year}"
    ).upper()
    drawing.text((540, 155), date_text, font=font(32), fill=text_color, anchor="mm")
    drawing.rectangle((435, 205, 645, 210), fill=text_color)

    quoted_text = f"“{quote}”"
    font_size = 56
    maximum_text_width = 760
    maximum_lines = 7

    while font_size >= 32:
        quote_font = font(font_size, True)
        lines = wrap_text_by_width(drawing, quoted_text, quote_font, maximum_text_width)
        line_height = int(font_size * 1.20)
        total_height = len(lines) * line_height
        if len(lines) <= maximum_lines and total_height <= 485:
            break
        font_size -= 2

    line_height = int(font_size * 1.20)
    total_height = len(lines) * line_height
    text_y = 520 - total_height / 2 + line_height / 2

    for line in lines:
        drawing.text((540, int(text_y)), line, font=quote_font, fill=text_color, anchor="mm")
        text_y += line_height

    theme = THEMES[index % len(THEMES)]
    drawing.text((540, 830), theme, font=font(25), fill=text_color, anchor="mm")
    drawing.line((455, 870, 625, 870), fill=text_color, width=2)
    drawing.text((540, 930), brand, font=font(34, True), fill=text_color, anchor="mm")

    output_path = "reflexion.png"
    image.save(output_path, format="PNG", optimize=True)
    return output_path, quote


def publish(path, caption):
    page_id = os.environ["FB_PAGE_ID"].strip()
    page_token = os.environ["FB_PAGE_TOKEN"].strip()
    api_version = os.getenv("FB_API_VERSION", "v25.0").strip()

    if not page_id:
        raise ValueError("El secreto FB_PAGE_ID está vacío.")
    if not page_token:
        raise ValueError("El secreto FB_PAGE_TOKEN está vacío.")

    boundary = "----Reflexiones2000"
    body = b""

    for key, value in [("caption", caption), ("access_token", page_token)]:
        body += (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{key}"\r\n\r\n'
            f"{value}\r\n"
        ).encode("utf-8")

    body += (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="source"; filename="reflexion.png"\r\n'
        "Content-Type: image/png\r\n\r\n"
    ).encode("utf-8")

    with open(path, "rb") as image_file:
        body += image_file.read()

    body += b"\r\n"
    body += f"--{boundary}--\r\n".encode("utf-8")

    endpoint = f"https://graph.facebook.com/{api_version}/{page_id}/photos"
    request = Request(
        endpoint,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        print("META_ERROR_STATUS:", error.code)
        print("META_ERROR_BODY:", detail)
        raise


def main():
    now = datetime.now(TZ)
    raw_index = os.getenv("IMAGE_INDEX", "").strip()

    if raw_index:
        try:
            image_index = int(raw_index) % 2000
        except ValueError as error:
            raise ValueError("IMAGE_INDEX debe ser un número entre 0 y 1999.") from error
    else:
        image_index = content_index(now)

    brand = os.getenv("BRAND", "Poema del Alma").strip() or "Poema del Alma"
    image_path, quote = render(now, image_index, brand)
    caption = f"{quote}\n\n#PoemaDelAlma #ReflexiónDelDía #Inspiración"
    result = publish(image_path, caption)

    print(json.dumps({"index": image_index, "image": image_path, "result": result}, ensure_ascii=False))


if __name__ == "__main__":
    main()
