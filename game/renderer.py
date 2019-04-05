import pygame
from pygame.locals import *

from game.grid import Grid
from game.playfield import ActiveBlock

class GridRenderer:
    """Base class for Grid rendering.
    
    Multiple renderers can be used to render a PlayField, so they could be
    thought of as "channels" or "layers."
    """

    def __init__(self, colors: tuple):
        """
        colors - Colors of each type of piece.
        """
        self.colors = colors

    def render(self, g: Grid, dest: pygame.Surface):
        """Render entire playfield."""
        raise NotImplementedError

    def update(self, g: Grid, dt: float):
        """Update renderer."""
        raise NotImplementedError


class BasicGridRenderer(GridRenderer):
    """Basic, solid color and outline, no effect, playfield.
    
    Each piece in the grid is and integer of what color it should be drawn as.
    For example, if you pass in colors as [[255, 0, 0]], a piece of value
    1 will represent the first element in colors, which is [255, 0, 0].
    """

    def __init__(self, colors: tuple):
        """
        colors - Color of blocks.
        """
        super().__init__(colors)

    def render(self, grid: Grid, dest: pygame.Surface):
        w = grid.get_width()
        h = grid.get_height()
        cell_w = dest.get_width() / w
        cell_h = dest.get_height() / h
        for y in range(h):
            for x in range(w):
                piece = grid.get_at(x, y)
                surf = pygame.Surface((cell_w, cell_h))
                if piece <= len(self.colors) and piece > 0:
                    # 0 means no color, 1 is the equivalent of colors[0]
                    surf.fill((255, 255, 255))
                    margin = int(.05 * cell_w)
                    surf.fill(self.colors[piece], pygame.Rect([margin] * 2,
                        (cell_w - margin, cell_h - margin)))
                dest.blit(surf, (x * cell_w, y * cell_h))

    def update(self, g: Grid, dt: float):
        pass # Nothing to update; no effects


class ShinyGridRenderer(GridRenderer):
    """Renderer that renders a shiny effect for each piece occasionally.
    
    This Renderer keeps its own equidimensional "grid" that contains
    values in which will determine the attributes of the shine for
    each piece.
    """

    def __init__(self, interval: int = 4):
        """
        inteval - In milliseconds, on when to trigger shiny effect.
        """
        super().__init__([]) # Only care about the shine effect, not coloring
        self.interval = interval

    def render(self, g: Grid, dest: pygame.Surface):
        pass

    def update(self, g: Grid, dt: float):
        """
        Update shine animation.
        """
        pass


class GhostRenderer(GridRenderer):
    """Renders 'ghost' block."""

    def __init__(self, colors: tuple, ab: ActiveBlock, opacity: float = .5):
        """
        """
        super().__init__(colors)
        self.opacity = opacity

    def render(self, g: Grid, dest: pygame.Surface):
        pass

    def update(self, g: Grid, dt: float):
        pass


class Renderers:
    """Keep a list of renderers to update and render in order."""

    def __init__(self, initial: list = []):
        self.renderers = initial[::]

    def update(self, g: Grid, dt: float):
        """Update all renderers."""
        for renderer in self.renderers:
            renderer.update(g, dt)

    def render(self, g: Grid, dest: pygame.Surface):
        """Render all renderer outputs to dest."""
        for renderer in self.renderers:
            renderer.render(g, dest)

    def add_renderer(self, r: GridRenderer):
        """Add a renderer to the stack."""
        self.renderers.append(r)
