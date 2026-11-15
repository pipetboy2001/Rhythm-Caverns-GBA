#!/usr/bin/env python3
"""Genera assets-src/social_preview.png (1280x640): la imagen de Social
Preview del repo de GitHub. No hay API para subirla (confirmado: GitHub
solo la deja cambiar desde Settings -> General -> Social preview) — este
script solo prepara el archivo, subirlo es un clic manual.

Composición: el anillo de golpe con un enemigo en cada carril (la propia
mecánica del juego) + el héroe al centro + el logo, todo con los sprites
y colores ya generados por el resto de assets-src/.

Correr desde esta carpeta: python make_social_preview.py
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
GFX = HERE.parent / "graphics"
W, H = 1280, 640

BG = (0x14, 0x0F, 0x24)
FLOOR = (0x23, 0x1B, 0x3F)
INK = (0xF2, 0xED, 0xFF)
GOLD = (0xFF, 0xC2, 0x3C)
LANES = [
    (0, -1, (0x3F, 0xD3, 0xC3), "enemy_bat"),      # arriba: teal
    (0, 1, (0xB1, 0x8F, 0xFF), "enemy_ghost"),     # abajo: violeta
    (-1, 0, (0xFF, 0x6A, 0x5C), "enemy_skeleton"), # izquierda: rojo
    (1, 0, (0xFF, 0xD0, 0x3A), "enemy_spider"),    # derecha: dorado
]


def load_sprite(name, scale):
    im = Image.open(GFX / f"{name}.bmp")
    pal = im.getpalette()
    rgba = Image.new("RGBA", im.size)
    rgba.putdata([(0, 0, 0, 0) if p == 0 else tuple(pal[p * 3:p * 3 + 3]) + (255,)
                  for p in im.getdata()])
    # Si tiene varios frames apilados verticalmente, usar solo el primero.
    if rgba.height > rgba.width:
        rgba = rgba.crop((0, 0, rgba.width, rgba.width))
    return rgba.resize((rgba.width * scale, rgba.height * scale), Image.NEAREST)


def main():
    out = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(out, "RGBA")

    # Layout horizontal (la tarjeta es 2:1): logo a la izquierda, la arena
    # con sus 4 carriles a la derecha. Todo el arte mantenido lejos de los
    # bordes con margen real, verificado a mano contra W/H.
    cx, cy = 900, H // 2
    radius = 150
    ring_r = 80

    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=FLOOR)
    for dx, dy, color, _ in LANES:
        ax, ay = cx + dx * radius, cy + dy * radius
        bx, by = cx + dx * (radius + 110), cy + dy * (radius + 110)
        draw.line((ax, ay, bx, by), fill=color + (60,), width=46)
    draw.ellipse((cx - ring_r - 3, cy - ring_r - 3, cx + ring_r + 3, cy + ring_r + 3),
                 outline=INK, width=3)
    for dx, dy, color, _ in LANES:
        angle = math.atan2(dy, dx)
        a0, a1 = math.degrees(angle - 0.4), math.degrees(angle + 0.4)
        draw.arc((cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r), a0, a1,
                  fill=color, width=8)

    # Héroe al centro, un enemigo por carril (la mecánica real del juego).
    hero = load_sprite("hero", 5)
    out.paste(hero, (cx - hero.width // 2, cy - hero.height // 2 - 10), hero)
    for dx, dy, _, enemy_name in LANES:
        sprite = load_sprite(enemy_name, 5)
        ex = cx + int(dx * (radius + 55)) - sprite.width // 2
        ey = cy + int(dy * (radius + 55)) - sprite.height // 2
        out.paste(sprite, (ex, ey), sprite)

    # Logo "RHYTHM CAVERNS" a la izquierda, mismo estilo que graphics/logo.bmp
    # (dorado con brillo, contorno tinta, sombra) pero renderizado grande y
    # nítido para la tarjeta en vez de a resolución de GBA.
    font = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", 92)
    lines = ["RHYTHM", "CAVERNS"]
    line_boxes = [font.getbbox(line) for line in lines]
    line_heights = [b[3] - b[1] for b in line_boxes]
    total_h = sum(line_heights) + 16
    ly = cy - total_h // 2 - 30
    lx_center = 300
    for line, box, lh in zip(lines, line_boxes, line_heights):
        lw = box[2] - box[0]
        lx = lx_center - lw // 2 - box[0]
        for ox, oy in ((-3, 3), (3, 3), (-3, -3), (3, -3), (0, 3), (0, -3), (3, 0), (-3, 0)):
            draw.text((lx + ox, ly + oy), line, font=font, fill=INK)
        draw.text((lx, ly), line, font=font, fill=GOLD)
        ly += lh + 28

    # Subtítulo debajo del logo, mismo bloque izquierdo.
    sub_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 26)
    subtitle = "A RHYTHM GAME FOR\nGAME BOY ADVANCE"
    draw.multiline_text((lx_center, ly + 30), subtitle, font=sub_font, fill=INK,
                         anchor="ma", align="center", spacing=10)

    out.save(HERE / "social_preview.png")
    print(HERE / "social_preview.png", out.size)


if __name__ == "__main__":
    main()
