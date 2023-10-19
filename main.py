from random import randint
import pygame
from pygame import Color, Vector2
from pygame.locals import QUIT, KEYUP, KEYDOWN, K_q, K_a, K_d, K_SPACE, KMOD_CTRL
from pygame.key import get_mods
from pygame.sprite import Group, spritecollide
import breakout

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
PADDLE_BOTTOM_MARGIN = 20
PADDLE_WIDTH, PADDLE_HEIGHT = 64, 16
FPS = 30
BLOCKS_TOP_MARGIN = 40
BLOCKS_SIDE_MARGINS = 40
BLOCK_SPACE_WIDTH, BLOCK_SPACE_HEIGHT = 30, 20
BLOCK_SPACE_MARGIN = 1
BLOCKS_PER_ROW = 25
BALL_RADIUS = 4
BALL_START_BOTTOM_MARGIN = 60
INITIAL_BALL_SPEED = 4
INITIAL_PADDLE_SPEED = 10
BALL_ACCELERATION_MODIFIER = 0.02
PADDLE_ACCELERATION_MODIFIER = 0.01

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
ball_speed = INITIAL_BALL_SPEED
paddle_speed = INITIAL_PADDLE_SPEED
ball_acceleration = 0.03
paddle_acceleration = 0.02
score = 0
points_multiplier = 1

boundaries = {
  "top": breakout.Boundary(0, -3, SCREEN_WIDTH, BALL_RADIUS),
  "left": breakout.Boundary(-3, 0, BALL_RADIUS, SCREEN_HEIGHT),
  "right": breakout.Boundary(SCREEN_WIDTH - 1, 0, BALL_RADIUS, SCREEN_HEIGHT),
  "bottom": breakout.Boundary(0, SCREEN_HEIGHT - 1, SCREEN_WIDTH, BALL_RADIUS)
}

breakout_blocks = Group()
blocks = []
block_colors = (Color(180, 0, 0), Color(255, 100, 0), Color(220, 220, 0),
                Color(80, 140, 0), Color(200, 200, 200), Color(0, 255, 0),
                Color(0, 220, 120), Color(0, 100,
                                          255), Color(0, 0,
                                                      200), Color(160, 0, 200))
for j, color in enumerate(block_colors):
  y = j * BLOCK_SPACE_HEIGHT + BLOCKS_TOP_MARGIN
  for i in range(BLOCKS_PER_ROW):
    x = i * BLOCK_SPACE_WIDTH + BLOCKS_SIDE_MARGINS
    block = breakout.BreakoutBlock(
      BLOCK_SPACE_WIDTH - (BLOCK_SPACE_MARGIN * 2),
      BLOCK_SPACE_HEIGHT - (BLOCK_SPACE_MARGIN * 2), color, (10 - j) * 10)
    block.x = x + BLOCK_SPACE_MARGIN
    block.y = y + BLOCK_SPACE_MARGIN
    blocks.append(block)

paddle = breakout.Paddle(PADDLE_WIDTH, PADDLE_HEIGHT)
ball = breakout.Ball(BALL_RADIUS)


def paddle_movement_correction():
  if paddle.movement.x != 0:
    if paddle.x - paddle.width / 2 < 0:
      paddle.x = paddle.width / 2
      paddle.movement.x = 0
    elif paddle.x + paddle.width / 2 > SCREEN_WIDTH:
      paddle.x = SCREEN_WIDTH - paddle.width / 2
      paddle.movement.x = 0


def reinitialize_blocks():
  breakout_blocks.empty()
  breakout_blocks.add(blocks)
  for b in breakout_blocks:
    b.show()
    b.draw(screen)
  pygame.display.update([b.rect for b in breakout_blocks])


paddle.y = SCREEN_HEIGHT - PADDLE_BOTTOM_MARGIN
paddle.x = SCREEN_WIDTH / 2
ball.x = SCREEN_WIDTH / 2
ball.y = SCREEN_HEIGHT - BALL_START_BOTTOM_MARGIN
ball.movement.x = -1 * ball_speed
ball.movement.y = 0
ball.movement.rotate_ip(randint(5, 175))
if ball.movement.y < -0.7:
  ball.movement.y = -0.7
  ball.movement.scale_to_length(ball_speed)

# to speed up event processing
pygame.event.set_blocked(None)
pygame.event.set_allowed([QUIT, KEYUP, KEYDOWN])

pygame.display.set_caption("BREAKOUT")
running = True

# initial loading and screen draw of blocks
reinitialize_blocks()

while running:
  for event in pygame.event.get():
    if event.type == QUIT or event.type == KEYUP and event.key == K_q and get_mods(
    ) & KMOD_CTRL:
      running = False
      break
    elif event.type == KEYDOWN and event.key in (K_a, K_d, K_SPACE):
      if event.key == K_a:
        paddle.movement.x = -1 * paddle_speed
      elif event.key == K_d:
        paddle.movement.x = paddle_speed
      else:
        paddle.movement.x = 0

  # for later Screen Drawing
  old_paddle_rect, old_ball_rect = paddle.rect.copy(), ball.rect.copy()

  # Sprite Movement
  paddle.update()
  ball.update()
  paddle_movement_correction()

  # Ball - Screen Boundary collision
  for name, boundary in boundaries.items():
    if boundary.rect.colliderect(ball.rect):
      if name == "bottom":
        running = False
        continue
      elif name == "top":
        ball.movement.y *= -1
        ball.y = ball.width / 2
      elif name == "left":
        ball.movement.x *= -1
        ball.x = ball.width / 2
      elif name == "right":
        ball.movement.x *= -1
        ball.x = SCREEN_WIDTH - ball.width / 2
      break

  # Ball - Paddle collision
  if ball.rect.colliderect(paddle.rect):
    if not breakout_blocks:
      # when all blocks are gone, reload and redraw the blocks and make game harder
      ball_acceleration += BALL_ACCELERATION_MODIFIER
      paddle_acceleration += PADDLE_ACCELERATION_MODIFIER
      ball_speed = INITIAL_BALL_SPEED
      paddle_speed = INITIAL_PADDLE_SPEED
      points_multiplier *= 2
      reinitialize_blocks()
    ball.movement.x, ball.movement.y = ball.x - paddle.x, ball.y - paddle.y
    ball.movement.scale_to_length(ball_speed)
    # ball bouncing off sides of paddle
    if abs(ball.movement.y) < 0.7:
      ball.movement.y = -0.7

  # Ball - Block(s) collisions
  collisions = spritecollide(ball, breakout_blocks, dokill=True)
  if collisions:
    for block in collisions:
      block.hide()
    block = collisions[0]
    old_movement = ball.movement.copy()
    dX = 2 * abs(ball.x - block.x) - block.width
    dY = 2 * abs(ball.y - block.y) - block.height
    if dX < 0 and dY < 0:
      mirror_vector = Vector2(ball.x - block.x, ball.y - block.y)
      reflection = ball.movement.reflect(mirror_vector)
      ball.movement.x, ball.movement.y = reflection.x, reflection.y
    else:
      if dX >= 0:
        ball.movement.x *= -1
      if dY >= 0:
        ball.movement.y *= -1
    score += sum([b.points * points_multiplier for b in collisions])
    ball_speed += ball_acceleration
    ball.movement.scale_to_length(ball_speed)
    paddle_speed += paddle_acceleration

  # Screen Drawing
  if collisions:
    block_redraws = [c.rect for c in collisions]
    for block in collisions:
      block.draw(screen)
    pygame.display.update(block_redraws)
  pygame.draw.rect(screen, (0, 0, 0), old_paddle_rect, 0)
  pygame.draw.rect(screen, (0, 0, 0), old_ball_rect, 0)
  paddle.draw(screen)
  ball.draw(screen)
  pygame.display.update(
    [old_paddle_rect, old_ball_rect, paddle.rect, ball.rect])

  clock.tick(FPS)

pygame.quit()
print("Final Score: ", score)
