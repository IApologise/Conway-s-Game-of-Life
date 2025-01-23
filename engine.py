import pygame
from copy import deepcopy
from objects import Cell


class Engine:
    def __init__(self, cell_size: int = 40):
        self.surface = pygame.display.set_mode((0, 0), pygame.WINDOWMAXIMIZED)
        self.size = self.surface.get_size()

        # Preparing grid
        self.grid_lines = []  # The lines
        lines = [int(self.size[0] / cell_size), int(self.size[1] / cell_size)]  # Counting lines
        self.grid_offset = [[(round(self.size[0] - lines[0] * cell_size) / 2), (round(self.size[1] - lines[1] * cell_size) / 2)],  # Origin
                            [(round(self.size[0] - lines[0] * cell_size) / 2), (round(self.size[1] - lines[1] * cell_size) / 2)],  # Local offset
                            [(round(self.size[0] - lines[0] * cell_size) / 2), (round(self.size[1] - lines[1] * cell_size) / 2)]]  # Global offset

        # Creating grid lines
        for dimension in range(2):
            for line in range(lines[0] + 1):

                # Evil math
                start_x = self.grid_offset[0][0] + cell_size * (dimension * (line + 1) - 1)
                end_x = self.grid_offset[0][0] + cell_size * (dimension * (line - 1) + 1) - self.size[0] * (dimension - 1)
                start_y = self.grid_offset[0][1] - cell_size * (dimension + line * (dimension - 1))
                end_y = self.grid_offset[0][1] + cell_size * (dimension - line * (dimension - 1)) + self.size[1] * dimension

                new_line = [[start_x, start_y], [end_x, end_y]]  # Assembling line
                self.grid_lines.append(new_line)  # Adding line to the list

        # Preparing cells
        self.cell_size = cell_size
        self.alive_cells = {}  # Position: Cell
        self.previous_steps = []  # Previous steps
        self.check = ((1, 0), (0, 1), (1, 1), (1, -1))  # Neighbours to check
        # 1,0 -> Right; 0,1 -> Up; 1,1 -> Right-Up; 1,-1 -> Right-Down

    def run(self, sps: int = 4) -> None:  # sps: steps per second

        # Clock
        Clock = pygame.time.Clock()
        step_event = pygame.USEREVENT + 1  # Step event
        pygame.time.set_timer(step_event, round(1000 / sps))
        move_event = pygame.USEREVENT + 2  # Move event
        pygame.time.set_timer(move_event, 2)

        render = True  # Pausing/Resuming graphics rendering
        step = False  # Pausing/Resuming the game
        running = True
        while running:  # Launching game
            Clock.tick(120)

            # Input sensor
            for event in pygame.event.get():

                # Checking if active
                if event.type != pygame.ACTIVEEVENT:
                    render = True  # Turning rendering back on if was off

                    # Tab
                    if event.type == pygame.QUIT:  # Stopping game
                        running, step, render = False, False, False
                    elif event.type == pygame.WINDOWMINIMIZED:  # Minimizing display
                        render = False
                        pygame.display.iconify()

                    # Keyboard
                    if event.type == pygame.KEYDOWN:

                        # Exiting game
                        if event.key == pygame.K_ESCAPE:
                            running, step, render = False, False, False

                        # Pausing the game
                        if event.key in [pygame.K_p, pygame.K_RETURN]:
                            if step:
                                step, render = False, False
                            else:
                                step, render = True, True

                        # Manually going up a step once
                        elif event.key == pygame.K_SPACE:
                            self.step_up()

                        # Clearing the grid
                        elif event.key in [pygame.K_c, pygame.K_DELETE]:
                            self.alive_cells.clear()

                        # Going back to the previous step
                        elif event.key == pygame.K_BACKSPACE:
                            self.step_down()

                    # Movement event
                    if event.type == move_event:
                        keys_pressed = pygame.key.get_pressed()  # Key press detector

                        # Moving up, down, left and right
                        if keys_pressed[pygame.K_w] or keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_s] or keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_d] or keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_a] or keys_pressed[pygame.K_LEFT]:
                            move = [0, 0]
                            if keys_pressed[pygame.K_w] or keys_pressed[pygame.K_UP]:
                                move[1] += 1
                            if keys_pressed[pygame.K_s] or keys_pressed[pygame.K_DOWN]:
                                move[1] -= 1
                            if keys_pressed[pygame.K_d] or keys_pressed[pygame.K_RIGHT]:
                                move[0] -= 1
                            if keys_pressed[pygame.K_a] or keys_pressed[pygame.K_LEFT]:
                                move[0] += 1

                            # Moving grid
                            for dimension in range(2):
                                self.grid_offset[2][dimension] += move[dimension]  # Applying changes to global
                                if self.grid_offset[1][dimension] <= 1 - self.cell_size:
                                    move[dimension] = -self.grid_offset[1][dimension]  # Calculating move distance for local
                                    self.grid_offset[2][dimension] += move[dimension] - (self.cell_size - 1)  # Moving global cells
                                elif self.grid_offset[1][dimension] >= self.cell_size - 1:
                                    move[dimension] = -self.grid_offset[1][dimension]  # Calculating move distance for local
                                    self.grid_offset[2][dimension] += move[dimension] + (self.cell_size - 1)  # Moving global cells (opposite)
                                self.grid_offset[1][dimension] += move[dimension]  # Moving local lines

                            # Moving lines
                            for line in self.grid_lines:
                                for point in line:
                                    for dimension in range(2):
                                        point[dimension] += move[dimension]  # Moving local

                    # Mouse
                    clicked = pygame.mouse.get_pressed()
                    if clicked[0] or clicked[2]:  # Left/Right

                        # Getting mouse position
                        x, y = pygame.mouse.get_pos()
                        position = (int((x - self.grid_offset[2][0]) / self.cell_size),
                                    int((y - self.grid_offset[2][1]) / self.cell_size))  # Approximating to grid

                        # Adding alive cells
                        if clicked[0]:
                            if position not in self.alive_cells:
                                new_cell = Cell(self.cell_size, True)
                                self.alive_cells.update({position: new_cell})

                        # Removing alive cells
                        elif clicked[2]:
                            try:
                                self.alive_cells.pop(position)
                            except KeyError:
                                pass

                # Customly timed movement in case of continued steps
                if event.type == step_event:

                    # Updating game objects
                    if step:
                        self.step_up()  # Going up a step

            # Rendering
            if render:
                self.render()  # Rendering game objects

    def step_up(self) -> None:
        self.previous_steps.append(deepcopy(self.alive_cells))  # Adding previous step to the list

        # Creating dead and counting neighbours
        dead_cells = {}  # Same structure as alive_cells
        for cell in self.alive_cells:
            for near_x in range(-1, 2):
                for near_y in range(-1, 2):
                    if not near_x and not near_y:
                        continue
                    neighbour = (cell[0] + near_x, cell[1] + near_y)
                    if neighbour in self.alive_cells:
                        self.alive_cells[cell].add_neighbour()
                        continue
                    elif neighbour not in dead_cells:
                        new_cell = Cell(self.cell_size, False)  # Creating a new dead cell
                        dead_cells.update({neighbour: new_cell})   # Adding cell to the dictionary
                    dead_cells[neighbour].add_neighbour()  # Adding itself as its neighbour

        # Checking alive cells
        remove_keys = []
        for cell in self.alive_cells:
            self.alive_cells[cell].step()  # Updating cell state
            if not self.alive_cells[cell].is_alive():  # Checking if still alive
                remove_keys.append(cell)  # If not -> Remove from the list
        for cell in remove_keys:
            self.alive_cells.pop(cell)  # Removing keys

        # Checking dead cells
        for cell in dead_cells:
            dead_cells[cell].step()  # Updating cell state
            if dead_cells[cell].is_alive():  # Checking if alive
                self.alive_cells.update({cell: dead_cells[cell]})  # Switching to alive dictionary

    def step_down(self) -> None:
        if self.previous_steps:
            self.alive_cells = self.previous_steps[-1]  # Loading step
            self.previous_steps.pop(-1)  # Removing redundant step from list

    def render(self) -> None:
        self.surface.fill((40, 40, 40))  # Drawing background

        # Drawing grid
        for line in self.grid_lines:
            pygame.draw.line(self.surface, (55, 55, 55), line[0], line[1], 1)

        # Drawing cells
        for position in self.alive_cells:
            self.alive_cells[position].draw(self.surface, self.size, position, self.grid_offset[2])

        pygame.display.flip()  # Updating display
