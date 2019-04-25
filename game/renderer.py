import pygame
from pygame.locals import *

from game.grid import Grid
from game.playfield import ActiveBlock
from game import util


def get_cell_dim(grid: Grid, dest: pygame.Surface) -> tuple:
    """Get proportionate cell dimensions."""
    w = grid.get_width()
    h = grid.get_height()
    #cell_w = dest.get_width() // w
    cell_h = dest.get_height() / h
    return cell_h, cell_h


class GridRenderer:
    """Base class for Grid rendering.
    
    Multiple renderers can be used to render a PlayField, so they could be
    thought of as "channels" or "layers."
    """

    def __init__(self, colors: tuple, g: Grid):
        """
        colors - Colors of each type of piece.
        """
        self.colors = colors
        self.grid = g
        self.surface = pygame.Surface((g.get_width(), g.get_height()))

    def render(self, dest: pygame.Surface):
        """Render entire playfield."""
        raise NotImplementedError

    def update(self, dt: float):
        """Update renderer."""
        raise NotImplementedError


class BasicGridRenderer(GridRenderer):
    """Basic, solid color and outline, no effect, playfield.
    
    Each piece in the grid is and integer of what color it should be drawn as.
    For example, if you pass in colors as [[255, 0, 0]], a piece of value
    1 will represent the first element in colors, which is [255, 0, 0].
    """

    def __init__(self, colors: tuple, g: Grid, alpha: int = 50):
        """
        colors - Color of blocks.
        alpha - Alpha transperancy value for ghost blocks.
        """
        super().__init__(colors, g)
        self.alpha = alpha

    def render(self, dest: pygame.Surface):
        w = self.grid.get_width()
        h = self.grid.get_height()
        pre_surf = pygame.Surface((w, h))

        for y in range(h):
            for x in range(w):
                piece = self.grid.get_at(x, y)
                surf = pygame.Surface((1, 1), pygame.SRCALPHA)
                if piece <= len(self.colors) and piece != 0:
                    # 0 means no color, 1 is the equivalent of colors[0]
                    # -1 is the equivalent to 1, but with alpha value
                    color = self.colors[abs(piece)][:]
                    if len(color) < 4 and piece < 0:
                        color.append(self.alpha)
                    surf.fill(color,
                        pygame.Rect(0, 0,
                            1, 1))
                pre_surf.blit(surf, (x, y))
        #target_dim = util.fit(pre_surf.get_rect(), dest.get_rect())
        dest.blit(util.resize(pre_surf, util.dimensions(dest.get_rect())), (0, 0))

    def update(self, dt: float):
        pass # Nothing to update; no effects
