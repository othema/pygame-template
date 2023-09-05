import pygame

cached_fonts = {}
cached_hover = {}
cached_buttons = {}

last_rect = None


class TextData:
    def __init__(self, x, y, width, height):
        self.x, self.y, self.w, self.h = x, y, width, height


def cache_font_name(name, size, bold=False, italic=False):
    return str(name) + str(size) + str(bold) + str(italic)


def cache(font, name):
    cached_fonts[name] = font
    return font


def get_font(name, size, bold=False, italic=False) -> pygame.font.Font:
    cname = cache_font_name(name, size, bold, italic)
    try:
        return cached_fonts[cname]
    except KeyError:
        try:
            return cache(pygame.font.Font(name, size), cname)
        except FileNotFoundError:
            return cache(pygame.font.SysFont(name, size, bold=bold, italic=italic), cname)


def text_world(game, txt, position, size=32, color=(255, 255, 255), font=None, aa=True, align="top-left", bold=False,
               italic=False, background=None):
    global last_rect
    surf = get_font(font, size, bold, italic).render(txt, aa, color, background)
    pos = align_font(position, align, surf)
    game.camera.blit(surf, pos)
    last_rect = pygame.Rect(*pos, *surf.get_size())
    return pygame.Rect(*pos, *surf.get_size())


def text_screen(game, txt, position, size=32, color=(255, 255, 255), font=None, aa=True, align="top-left", bold=False,
                italic=False, background=None):
    global last_rect
    surf = get_font(font, size, bold, italic).render(txt, aa, color, background)
    pos = align_font(position, align, surf)
    game.wn.blit(surf, pos)
    last_rect = pygame.Rect(*pos, *surf.get_size())
    return pygame.Rect(*pos, *surf.get_size())


def text_surf(dest, txt, position, size=32, color=(255, 255, 255), font=None, aa=True, align="top-left", bold=False,
              italic=False, background=None):
    global last_rect
    surf = get_font(font, size, bold, italic).render(txt, aa, color, background)
    pos = align_font(position, align, surf)
    dest.blit(surf, pos)
    last_rect = pygame.Rect(*pos, *surf.get_size())
    return pygame.Rect(*pos, *surf.get_size())


def text_data(txt, position, size=32, font=None, align="top-left", bold=False, italic=False) -> TextData:
    surf = get_font(font, size, bold, italic).render(txt, False, (0, 0, 0))
    pos = align_font(position, align, surf)
    data = TextData(*pos, surf.get_width(), surf.get_height())
    return data


def button(game, txt, position, size=32, text_color=(0, 0, 0), bg_color=(255, 255, 255), bg_color_hover=(230, 230, 230),
           font=None, aa=True, align="top-left", text_align="center", padding=5, border_radius=0, bold=False,
           italic=False, width=None, hover_sound=None, disabled=False):
    global last_rect

    data = text_data(txt, position, size, font, "top-left", bold, italic)
    button_width = data.w + padding * 2 if width is None else width
    button_rect = pygame.Rect(data.x, data.y, button_width, data.h + padding * 2)

    surf = pygame.Surface(button_rect.size, pygame.SRCALPHA)
    align_button = align_font(button_rect.topleft, align, surf)
    hovered = not disabled and pygame.Rect(*align_button, button_width, button_rect.h).collidepoint(*pygame.mouse.get_pos())
    color = bg_color_hover if hovered else bg_color

    pygame.draw.rect(surf, color, (0, 0, *surf.get_size()), border_radius=border_radius)
    text_x = {
        "left": padding,
        "center": button_width / 2,
        "right": button_width - padding
    }[text_align]
    text_surf(surf, txt, (text_x, padding), size, text_color, font, aa, "top-" + text_align, bold, italic)
    game.wn.blit(surf, align_button)

    cname = cache_font_name(txt + str(button_rect), size, bold, italic)
    try:
        if cached_hover[cname] and not hovered:  # just ended hovering
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        elif not cached_hover[cname] and hovered:  # just started hovering
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            if hover_sound is not None: hover_sound.play()
    except KeyError:
        pass
    cached_hover[cname] = hovered

    last_rect = pygame.Rect(*align_button, *surf.get_size())

    return hovered and game.just_mouse_up


def align_font(position, align, surf) -> list:
    pos = list(position)
    split = align.split("-")

    if split[0] == "bottom":
        pos[1] -= surf.get_height()
    elif split[0] == "center":
        pos[1] -= surf.get_height() / 2

    if split[1] == "right":
        pos[0] -= surf.get_width()
    elif split[1] == "center":
        pos[0] -= surf.get_width() / 2

    return pos


def _bar(rect: pygame.Rect, progress, total=100, bar_color=(0, 255, 0), bg_color=(30, 30, 30), text_center=False):
    surf = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(surf, bg_color, (0, 0, *rect.size))
    pygame.draw.rect(surf, bar_color, (0, 0, rect.w*(progress/total), rect.h))
    text_pos = (rect.w/2, rect.h/2) if text_center else (5, rect.h/2)
    text_surf(surf, f"{progress}/{total}", text_pos, max(18, rect.h-15), align="center-center" if text_center else "center-left")
    return surf


def bar_surf(surf, rect: pygame.Rect, progress, total=100, bar_color=(0, 255, 0), bg_color=(30, 30, 30), text_center=False):
    bar = _bar(rect, progress, total, bar_color, bg_color, text_center)
    surf.blit(bar, rect.topleft)


def bar_world(game, rect: pygame.Rect, progress, total=100, bar_color=(0, 255, 0), bg_color=(30, 30, 30), text_center=False):
    game.camera.blit(_bar(rect, progress, total, bar_color, bg_color, text_center), rect.topleft)


def darken(color, amount=15):
    new = []
    for value in color:
        new.append(min(255, max(0, value - amount)))
    return tuple(new)
