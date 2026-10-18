import json
import os
import textwrap

from datetime import date, datetime
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont


TZ = ZoneInfo("America/Mexico_City")

DAYS = [
    "lunes",
    "martes",
    "miércoles",
    "jueves",
    "viernes",
    "sábado",
    "domingo",
]

MONTHS = [
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
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
    ("#203b59", "#8e718d", "#ffffff"),
    ("#174d43", "#70a983", "#fff9df"),
    ("#422f58", "#c57873", "#fff4ed"),
    ("#3b402d", "#c7aa67", "#ffffed"),
    ("#1e4b5b", "#67a8a3", "#f4ffff"),
    ("#72452c", "#d5ae68", "#fff8e8"),
    ("#34304f", "#8993cf", "#fff7ff"),
    ("#384f34", "#adb66b", "#fbffe9"),
    ("#4d3443", "#d793aa", "#fff3f8"),
]

THEMES = [
    "GRATITUD",
    "ESPERANZA",
    "VIDA",
    "FE",
    "SUPERACIÓN",
    "FAMILIA",
    "NATURALEZA",
    "PROPÓSITO",
]


def font(size, bold=False):
    if bold:
        font_path = (
            "/usr/share/fonts/truetype/dejavu/"
            "DejaVuSerif-Bold.ttf"
        )
    else:
        font_path = (
            "/usr/share/fonts/truetype/dejavu/"
            "DejaVuSerif.ttf"
        )

    return ImageFont.truetype(font_path, size)


def hex_to_rgb(color):
    return tuple(
        int(color[position:position + 2], 16)
        for position in (1, 3, 5)
    )


def content_index(now):
    """
    Selecciona uno de cuatro índices diarios según la hora local.

    Horarios:
    08:00
    12:00
    16:00
    20:00

    Con cuatro publicaciones al día, las 2,000 combinaciones
    cubren 500 días antes de iniciar nuevamente el ciclo.
    """

    publication_hours = [8, 12, 16, 20]

    slot = min(
        range(len(publication_hours)),
        key=lambda index: abs(
            now.hour - publication_hours[index]
        ),
    )

    elapsed_days = (
        now.date() - date(2026, 1, 1)
    ).days

    return ((elapsed_days * 4) + slot) % 2000


def make_quote(index):
    """
    Produce exactamente 2,000 combinaciones:

    10 aperturas x 20 ideas centrales x 10 cierres.
    """

    normalized_index = index % 2000

    opening = OPEN[normalized_index // 200]
    core = CORE[(normalized_index // 10) % 20]
    closing = CLOSE[normalized_index % 10]

    return f"{opening} {core}, {closing}."


def render(now, index, brand):
    quote = make_quote(index)

    first_color, second_color, text_color = PALETTES[
        index % len(PALETTES)
    ]

    start_rgb = hex_to_rgb(first_color)
    end_rgb = hex_to_rgb(second_color)

    image = Image.new(
        "RGB",
        (1080, 1080),
    )

    pixels = image.load()

    for y_position in range(1080):
        transition = y_position / 1079

        current_color = tuple(
            int(
                start_rgb[channel] * (1 - transition)
                + end_rgb[channel] * transition
            )
            for channel in range(3)
        )

        for x_position in range(1080):
            pixels[x_position, y_position] = current_color

    drawing = ImageDraw.Draw(
        image,
        "RGBA",
    )

    drawing.rectangle(
        (60, 60, 1020, 1020),
        fill=(0, 0, 0, 82),
    )

    date_text = (
        f"{DAYS[now.weekday()]} "
        f"{now.day} de "
        f"{MONTHS[now.month - 1]} de "
        f"{now.year}"
    ).upper()

    drawing.text(
        (540, 165),
        date_text,
        font=font(34),
        fill=text_color,
        anchor="mm",
    )

    drawing.rectangle(
        (430, 220, 650, 225),
        fill=text_color,
    )

    # Decoración variable según el índice.
    for decoration_index in range(16):
        x_position = (
            decoration_index * 137
            + index * 29
        ) % 1080

        y_position = (
            90
            + (decoration_index % 6) * 170
        )

        radius = (
            18
            + (
                index
                + decoration_index * 7
            ) % 42
        )

        drawing.ellipse(
            (
                x_position - radius,
                y_position - radius,
                x_position + radius,
                y_position + radius,
            ),
            outline=text_color,
            width=2,
        )

    quoted_text = f"“{quote}”"
    font_size = 64

    lines = textwrap.wrap(
        quoted_text,
        width=29,
    )

    while len(lines) > 7 and font_size > 40:
        font_size -= 3

        lines = textwrap.wrap(
            quoted_text,
            width=31,
        )

    line_height = int(font_size * 1.28)

    text_y = (
        520
        - ((len(lines) - 1) * line_height / 2)
    )

    for line in lines:
        drawing.text(
            (540, text_y),
            line,
            font=font(font_size, True),
            fill=text_color,
            anchor="mm",
        )

        text_y += line_height

    theme = THEMES[
        index % len(THEMES)
    ]

    drawing.text(
        (540, 835),
        theme,
        font=font(27),
        fill=text_color,
        anchor="mm",
    )

    drawing.text(
        (540, 935),
        brand,
        font=font(36, True),
        fill=text_color,
        anchor="mm",
    )

    output_path = "reflexion.png"

    image.save(
        output_path,
        format="PNG",
        optimize=True,
    )

    return output_path, quote


def publish(path, caption):
    page_id = os.environ["FB_PAGE_ID"].strip()
    page_token = os.environ["FB_PAGE_TOKEN"].strip()

    api_version = os.getenv(
        "FB_API_VERSION",
        "v25.0",
    ).strip()

    if not page_id:
        raise ValueError(
            "El secreto FB_PAGE_ID está vacío."
        )

    if not page_token:
        raise ValueError(
            "El secreto FB_PAGE_TOKEN está vacío."
        )

    boundary = "----Reflexiones2000"
    body = b""

    fields = [
        ("caption", caption),
        ("access_token", page_token),
    ]

    for key, value in fields:
        body += (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; '
            f'name="{key}"\r\n\r\n'
            f"{value}\r\n"
        ).encode("utf-8")

    body += (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; '
        f'name="source"; '
        f'filename="reflexion.png"\r\n'
        f"Content-Type: image/png\r\n\r\n"
    ).encode("utf-8")

    with open(path, "rb") as image_file:
        body += image_file.read()

    body += b"\r\n"
    body += (
        f"--{boundary}--\r\n"
    ).encode("utf-8")

    endpoint = (
        f"https://graph.facebook.com/"
        f"{api_version}/"
        f"{page_id}/photos"
    )

    request = Request(
        endpoint,
        data=body,
        headers={
            "Content-Type": (
                f"multipart/form-data; "
                f"boundary={boundary}"
            ),
        },
        method="POST",
    )

    try:
        with urlopen(
            request,
            timeout=60,
        ) as response:
            response_text = response.read().decode(
                "utf-8"
            )

            return json.loads(response_text)

    except HTTPError as error:
        detail = error.read().decode(
            "utf-8",
            errors="replace",
        )

        print(
            "META_ERROR_STATUS:",
            error.code,
        )

        print(
            "META_ERROR_BODY:",
            detail,
        )

        raise


def main():
    now = datetime.now(TZ)

    raw_index = os.getenv(
        "IMAGE_INDEX",
        "",
    ).strip()

    if raw_index:
        try:
            image_index = int(raw_index) % 2000

        except ValueError as error:
            raise ValueError(
                "IMAGE_INDEX debe ser un número "
                "entre 0 y 1999."
            ) from error

    else:
        image_index = content_index(now)

    brand = os.getenv(
        "BRAND",
        "Poema del Alma",
    ).strip()

    if not brand:
        brand = "Poema del Alma"

    image_path, quote = render(
        now,
        image_index,
        brand,
    )

    caption = (
        f"{quote}\n\n"
        "#PoemaDelAlma "
        "#ReflexiónDelDía "
        "#Inspiración"
    )

    result = publish(
        image_path,
        caption,
    )

    output = {
        "index": image_index,
        "image": image_path,
        "result": result,
    }

    print(
        json.dumps(
            output,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
