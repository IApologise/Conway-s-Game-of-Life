import pygame


class Cell:
    def __init__(self, size: int, state: bool = False):
        self.drawing_offset = 2  # Reducing size to make more visible (in pixels)
        self.hitbox_size = size  # Size of the space cell occupies in grid (in pixels)
        self.drawing_size = self.hitbox_size - self.drawing_offset * 2  # Size of the cell when drawn (in pixels)

        self.state = state   # Alive/Dead
        self.neighbours = 0  # Alive neighbours

    def is_alive(self) -> bool:
        return self.state

    def add_neighbour(self) -> None:
        self.neighbours += 1

    def step(self) -> None:
        if self.state:
            if self.neighbours < 2:  # Dead ;(
                self.state = False
            elif self.neighbours > 3:  # Dead ;(
                self.state = False
        elif self.neighbours == 3:  # Alive :D
            self.state = True
        self.neighbours = 0  # Resetting counter

    def draw(self, surface: pygame.surface.Surface, surface_size: tuple[int, int], position: list[int, int], offset: list[int, int]) -> None:
        if self.state:
            grid_position = [position[0] * self.hitbox_size + self.drawing_offset + offset[0],  # X
                             position[1] * self.hitbox_size + self.drawing_offset + offset[1]]  # Y
            if surface_size[0] + self.hitbox_size > grid_position[0] > -self.hitbox_size:      # Checking if in x
                if surface_size[1] + self.hitbox_size > grid_position[1] > -self.hitbox_size:  # Checking if in y
                    shape = pygame.Rect(grid_position[0], grid_position[1], self.drawing_size, self.drawing_size)
                    pygame.draw.rect(surface, (200, 200, 200), shape)  # Rendering
