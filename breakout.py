import pygame
from pygame import Vector2
from pygame.sprite import Sprite
from pygame import Color, Rect


class SimpleBlock(Sprite):
  """Represents a simple block object in PyGame"""

  def __init__(self, width: int = None, height: int = None, /, color="black"):
    super().__init__()
    if width is None or height is None or width < 1 or height < 1:
      raise RuntimeError("width and height must be positive integers")
    self._image = pygame.Surface((width, height))
    self._move = Vector2(0, 0)
    self._hitbox = self._image.get_rect()
    self._color = color
    self._image.fill(color)

  @property
  def image(self):
    return self._image

  @property
  def rect(self):
    return self._hitbox

  @property
  def x(self):
    return self._hitbox.centerx

  @x.setter
  def x(self, value: int):
    self._hitbox.centerx = value

  @property
  def y(self):
    return self._hitbox.centery

  @y.setter
  def y(self, value: int):
    self._hitbox.centery = value

  @property
  def width(self):
    return self._hitbox.width

  @property
  def height(self):
    return self._hitbox.height

  @property
  def movement(self):
    return self._move

  @property
  def color(self):
    return self._color

  @color.setter
  def color(self, value: Color | str):
    self._color = value
    self._image.fill(self._color)

  def update(self, *args, **kwargs):
    self._hitbox.x += self._move.x
    self._hitbox.y += self._move.y

  def draw(self, screen):
    screen.blit(self._image, self._hitbox)


class StaticBlock(SimpleBlock):
  """Represents a stationary block"""

  def __init__(self,
               width: int = None,
               height: int = None,
               color: Color = None):
    if color is None:
      raise RuntimeError("color parameter must be a pyGame Color instance")
    super().__init__(width, height, color)
    self._move = None

  def movement(self):
    return None

  def update(self, *args, **kwargs):
    return


class BreakoutBlock(StaticBlock):
  """Represents a breakout block"""

  def __init__(self,
               width: int = None,
               height: int = None,
               color: Color = None,
               points: int = 0):
    super().__init__(width, height, color)
    self._points = points
    self._hidden = False

  @property
  def points(self):
    return self._points

  def hide(self):
    self._hidden = True

  def show(self):
    self._hidden = False

  def draw(self, screen):
    if not self._hidden:
      super().draw(screen)
      return
    pygame.draw.rect(screen, (0, 0, 0), self._hitbox, 0)


class Ball(SimpleBlock):
  """Represents a moving ball"""

  def __init__(self, radius: int = None, /):
    if radius is None or radius < 1:
      raise RuntimeError("radius must be positive integers")
    color = "white"
    super().__init__(radius, radius, color)

  def draw(self, screen):
    super().draw(screen)


class Paddle(SimpleBlock):
  """Represents a moving paddle"""

  def __init__(self, width: int = None, height: int = None, /):
    super().__init__(width, height, "white")


class Boundary:
  """Represents an invisible area. Useful for collision detection"""

  def __init__(self,
               x: int = None,
               y: int = None,
               width: int = None,
               height: int = None):
    super().__init__()
    if x is None or y is None:
      raise RuntimeError("x and y must be integers")
    if width is None or height is None or width < 1 or height < 1:
      raise RuntimeError("width and height must be positive integers")
    self._hitbox = Rect(x, y, width, height)

  @property
  def rect(self):
    return self._hitbox

  @property
  def x(self):
    return self._hitbox.x

  @x.setter
  def x(self, value: int):
    self._hitbox.x = value

  @property
  def y(self):
    return self._hitbox.y

  @y.setter
  def y(self, value: int):
    self._hitbox.y = value

  @property
  def width(self):
    return self._hitbox.width

  @property
  def height(self):
    return self._hitbox.height
