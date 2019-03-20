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
        padding_x: float = .005, padding_y: float = .005,
        title_height: float = .3, color: tuple = (255, 255, 255)):
        """
        x - X coordinate.
        y - Y coordinate.
        width - Width of display.
        height - Height of display.
        background - Background Surface.
        title - Optional title. Leave empty string to have only content.
        font - Font for title.
        padding_x - X padding percentage of width.
        padding_y - Y padding percentage of height.
        title_height - Height of title percentage of height.
        color - Color of title text.
        """
        super().__init__()
        self.background = background
        self.rect = pygame.Rect(x, y, width, height)
        self.image = self._get_background()
        self.padding_x = padding_x
        self.padding_y = padding_y

        self.title = title
        self.font = font
        self.title_height = title_height
        self.color = color # Text color
        self.content = None  # Surface to display
        self.remaining_h = 0 # Remaining height left for content
        self.remaining_w = 0 # Remaining width left for content
        self.content_rect = pygame.Rect(0, 0, 0, 0)

        self.redraw()

    def redraw(self): # TODO: optimize
        """Redraw all assets in the HUD."""
        self.clear_everything()
        total_remaining_h = self.rect.height - self.padding_height() * 2
        total_remaining_w = self.rect.width - self.padding_width() * 2

        if self.font is not None or self.text is not "":
            title = Text(self.title, self.font, color=self.color)
            # Available space for any assets (within margins)
            available = pygame.Rect(self.padding_width(), self.padding_height(),
                self.rect.width - self.padding_width(),
                self.rect.height - self.padding_height())
            # Fit into header
            if self.content:  # Adjust to reserve space for content
                header = pygame.Rect(available.x, available.y,
                    available.width, available.height * self.title_height)
                title.rect = util.fit(title.rect, header)
            self.image.blit(title.image, title.rect)

        self.content_rect.x = self.padding_width()
        self.content_rect.y = title.rect.y + title.rect.height
        self.content_rect.width = available.width
        self.content_rect.height = available.height
        #self.redraw_content()
        self.dirty = 1

    def redraw_content(self):
        """Redraw only the content.
        if self.content is not None:
            self.content_rect = util.fit(self.content.get_rect(),
                self.image.get_rect())
            self.image.blit(self.content, self.content_rect)"""
        self.redraw()

    def update_content(self, ncont: pygame.Surface):
        """Update the content Surface and redraw."""
        self.content = ncont
        self.redraw_content()

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
