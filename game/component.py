# Collection of handy components for UI
import pygame
from pygame.locals import *

from game import util


class Text(pygame.sprite.DirtySprite):

    def __init__(self, txt: str, font: pygame.font.Font,
        antialias: bool = True, color = (255, 255, 255),
        background = None):
        """
        txt - Initial text..
        font - Font to render.
        antialias - Smooth rendering?
        color - Foreground color RGB(A).
        background - Background color RGB(A).
        """
        super().__init__()
        self._font = font
        self._text = txt
        self.antialias = antialias
        self.color = color
        self.background = background

        self.set_font(font)
        self.image = self._render(txt, antialias, color, background)
        self.rect = self.image.get_rect()
        self.dirty = 1

    def get_text(self) -> str:
        """Get current text."""
        return self._text

    def set_text(self, txt: str):
        """Set the current text displayed."""
        self._text = txt
        self.image = self._render(txt, self.antialias, self.color,
            self.background)
        self.dirty = 1

    def set_font(self, font: pygame.font.Font):
        """Set the currently used font."""
        assert font is not None
        self._font = font
        self.set_text(self.get_text())

    def get_font(self) -> pygame.font.Font:
        """Get currently used font."""
        return self._font

    def _render(self, txt: str, aa: bool, fg, bg) -> pygame.Surface:
        """Return rendered text on a Surface."""
        return self._font.render(txt, aa, fg, bg)

    def get_width(self) -> int:
        return self.image.get_width()

    def get_height(self) -> int:
        return self.image.get_height()


class HUDDisplay(pygame.sprite.DirtySprite):
    """A single HUD info display."""

    def __init__(self, x: int, y: int, width: int, height: int,
        background: pygame.Surface, content: pygame.Surface = None,
        title: str = "", font: pygame.font.Font = None,
        proportion: bool = True,
        title_height: float = .25, color: tuple = (255, 255, 255)):
        """
        x - X coordinate.
        y - Y coordinate.
        width - Width of display.
        height - Height of display.
        background - Background Surface.
        title - Optional title. Leave empty string to have only content.
        font - Font for title.
        proportion - Keep content proportionate to display area?
        title_height - Height of title percentage of height.
        color - Color of title text.
        """
        super().__init__()
        self.background = background
        self.rect = pygame.Rect(x, y, width, height)
        self.image = self._get_background()

        self.title = title
        self.font = font
        self.proportion = proportion
        self.title_height = title_height
        self.color = color # Text color
        self.content = content  # Surface to display

        self.redraw()

    def redraw(self):
        """Redraw all assets."""
        self.clear_everything()
        # Size and draw text
        remaining_height = self.rect.height
        y_offset = 0 # Y Offset for content
        if self.font and self.title != "":
            rendered = self.font.render(self.title, True, self.color)
            true_h = remaining_height * self.title_height
            resized = util.fit(
                rendered.get_rect(),
                pygame.Rect(0, 0, self.rect.width, true_h)
                )
            y_offset = resized.height
            rendered = util.resize(rendered, util.dimensions(resized))
            self.image.blit(rendered, (0, 0))

        # Size and draw content
        if self.content:
            resized = util.fit(
                self.content.get_rect(),
                pygame.Rect(0, 0, self.rect.width, remaining_height),
                self.proportion
                )
            rendered = util.resize(self.content, util.dimensions(resized))
            self.image.blit(rendered, (0, y_offset))
        self.dirty = 1

    def update_content(self, ncont: pygame.Surface):
        """Update the content Surface and redraw."""
        self.content = ncont
        self.redraw()

    def padding_width(self) -> int:
        """Get the padding width."""
        return self.rect.width * self.padding_x

    def padding_height(self) -> int:
        """Get the padding height."""
        return self.rect.height * self.padding_y

    def _get_background(self) -> pygame.Surface:
        """Get the background surface."""
        rect = util.dimensions(self.rect)
        if self.background:
            return util.resize(self.background, rect)
        return pygame.Surface(rect)

    def clear_everything(self):
        """Clear everything, and just have an empty board with background."""
        self.image = self._get_background()
        self.dirty = 1
