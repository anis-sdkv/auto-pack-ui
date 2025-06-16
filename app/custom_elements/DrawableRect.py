from random import randint
from typing import Tuple

import pygame


# class DrawableRect:
#     _id_counter = 0
#
#     def __init__(self, rect: pygame.Rect, angle: float = 0, image=None,
#                  back_color: Tuple[int, int, int] = None, rect_id=None):
#         self.rect: pygame.Rect = rect
#         self.angle = angle
#         self.image = image
#         if back_color is None:
#             back_color = [randint(0, 255) for _ in range(3)]
#         self.back_color = back_color
#
#         if rect_id is None:
#             self.rect_id = DrawableRect._id_counter
#             DrawableRect._id_counter += 1
#         else:
#             self.rect_id = rect_id
