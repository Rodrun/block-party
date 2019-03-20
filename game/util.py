from copy import copy
import pygame


MULTIPLIER = [40, 100, 300, 1200]


def get_points(level: int, lines_cleared: int) -> int:
    """Calculate points from lines cleared."""
    points = 0
    if lines_cleared > 0 and lines_cleared <= 4:
        points = MULTIPLIER[lines_cleared - 1] * (level + 1)
    return points


def resize(sfc: pygame.Surface, dim: tuple) -> pygame.Surface:
    """Wrapper for pygame's scale transformation."""
    return pygame.transform.scale(sfc, [x for x in integerify(dim)])


def integerify(target):
    """Convert each element of an iterable into an integer."""
    for e in target:
        yield int(e)


def dimensions(rect: pygame.Rect) -> tuple:
    """Get the dimensions of a Rect as a tuple of length 2."""
    return rect.width, rect.height


def fit(srcRect: pygame.Rect, destRect: pygame.Rect,
    proportionKeep: bool = True) -> pygame.Rect:
    """Find dimensions of a rect that will fit into another.

    srcRect - Source Rect.
    destRect - Destination Rect to fit into.
    proportionKeep - Maintain aspect ratio? If false, will fill to destRect.
    """
    result = copy(destRect)
    if proportionKeep:
        ratio = min([destRect.height / srcRect.height, destRect.width / srcRect.width])
        result.width = srcRect.width * ratio
        result.height = srcRect.height * ratio
    return result


def format_int(n: int, zeros: int = 7) -> str:
    """Format integer as zero-filled string."""
    return str(n).zfill(zeros)
