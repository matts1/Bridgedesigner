import sys
import pygame
import string
from vectors import Vector
import math
import time

ALPHABET = string.uppercase + string.lowercase
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1000
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

TENSION = 1
COMPRESSION = 2

LCLICK = 1
MCLICK = 2
RCLICK = 3

class Bridge(object):
    def __init__(self, filename):
        try:
            lines = open(filename, "rU").readlines()
        except IOError:
            lines = ["1", "1000"]

        self.filename = filename
        self.height_div = float(lines[0])
        self.width = float(lines[1])

        self.load = 1 # mass (kg)

        self.lowerx = -0.1 * self.width
        self.upperx = 1.1 * self.width
        self.lowery = -0.1 * self.get_height(self.width)
        self.uppery = 1.1 * self.get_height(self.width)

        self.centre = CentreNode(self.width, self)

        lines = map(float, ["0"] + lines[2:])
        self.nodes = [Node(x, self) for x in lines]

        self.pressed = {}

        self.calc()

        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.close = False
        self.lastframe = 0

        while not self.close:
            self.update()
            self.draw()
        self.save()
        self.quit()

    def calc(self):
        assert self.nodes[-1].x == self.width
        # LHS of bridge is taking 1/2 of vert load, 0 horizontal load
        down = Vector((0, 4.9 * self.load))

        for i, node in enumerate(self.nodes[:-1]):
            node.down = down
            node.up = Vector(self.nodes[i + 1]) - Vector(node)
            node.side = Vector(node) - Vector(self.centre)
            node.side = node.side.scale(
                    node.down.size() * (node.down.cos() * node.up.tan() - node.down.sin()) /\
                    (node.side.cos() * node.up.tan() + node.side.sin())
            )
            node.up = node.up.scale(
                (node.down.size() * node.down.sin() - node.side.size() * node.side.sin()) /\
                node.up.sin()
            )
            down = node.up # below the next node is above us

        self.nodes[-1].down = self.nodes[-1].up = self.nodes[-2].up
        self.nodes[-1].up[0] *= -1 # invert the x axis on the opposite side
        self.nodes[-1].side = Vector((0, -2 * self.nodes[-1].down[1]))



    def get_height(self, x):
        highest = self.width ** 2
        diff = (self.width - x) ** 2
        return (highest - diff) / self.height_div

    def update(self):
        for key in self.pressed:
            if self.pressed[key] > 0:
                self.pressed[key] += 1
            elif self.pressed[key] < 0:
                self.pressed[key] -= 1
        dx, dy = pygame.mouse.get_rel()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
                    (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.close = True
                return
            if event.type == pygame.KEYDOWN:
                self.pressed[event.key] = 1
                if event.key == pygame.K_DELETE:
                    newnodes = []
                    for node in self.nodes:
                        if not node.selected:
                            newnodes.append(node)
                    self.nodes = newnodes
                if event.key == pygame.K_INSERT:
                    x = pygame.mouse.get_pos()[0]
                    x = self.width * (x - SCREEN_WIDTH / 12) / (SCREEN_WIDTH / 1.2)
                    self.nodes.append(Node(x, self))
                    self.nodes.sort(key=lambda n: n.x)
            elif event.type == pygame.KEYUP:
                self.pressed[event.key] = 0
            elif event.type == pygame.MOUSEBUTTONUP:
                self.pressed[-event.button] = 0
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.pressed[-event.button] = 1
                if event.button == RCLICK:
                    for node in self.nodes:
                        node.selected = False
                if event.button in (LCLICK, RCLICK):
                    for node in self.nodes[1:-1]:
                        if (Vector(self.get_coords(node)) - Vector(pygame.mouse.get_pos())).size() < 5:
                            if event.button == RCLICK:
                                node.selected = True
                            elif event.button == LCLICK:
                                node.selected = not node.selected
        if self.pressed.get(-MCLICK, 0):
            change = 1.2 * self.width / SCREEN_WIDTH * dx
            for i, node in enumerate(self.nodes):
                if node.selected: # only 1:-1 can be selected, so no indexerror
                    node.x += change
            for i, node in enumerate(self.nodes):
                if node.selected:
                    prev = self.nodes[i - 1]
                    after = self.nodes[i + 1]
                    if after.x <= node.x:
                        node.x = after.x - 1
                    if prev.x >= node.x and not (prev.selected and change > 0):
                        node.x = prev.x + 1

        l = self.pressed.get(pygame.K_LEFT, 0)
        r = self.pressed.get(pygame.K_RIGHT, 0)
        if bool(l) != bool(r):
            move = 1 if r else -1
            held = max(l, r)
            for node in self.nodes:
                if (held == 1 or held > 30) and node.selected and (node.x + move not in [n.x for n in self.nodes]):
                    node.x += move

        self.calc()
        self.draw()

    def get_axis_coord(self, lower, num, upper, highest):
        return int((num - lower) / (upper - lower) * highest)

    def get_coords(self, coords):
        if isinstance(coords, Node):
            coords = (coords.x, coords.get_height())
        return (self.get_axis_coord(self.lowerx, coords[0], self.upperx, SCREEN_WIDTH),
                self.get_axis_coord(self.lowery, self.get_height(self.width) - coords[1],
                        self.uppery, SCREEN_HEIGHT))

    def drawmember(self, start, end):
        pygame.draw.line(self.screen, BLACK, start, end)

    def draw(self):
        self.screen.fill(WHITE)
        centre = self.centre.draw(self.screen, len(self.nodes))
        old = new = None
        font = pygame.font.Font(None, 20)
        for i, node in enumerate(self.nodes):
            old = new
            new = node.draw(self.screen, i)
            self.drawmember(new, centre)
            pos = (Vector(new) + Vector(centre)) / 2
            dis = (Vector(node) - Vector(self.centre)).size()
            self.screen.blit(
                font.render(
                    getstats(node.side.size(), dis, TENSION),
                    1, BLACK
                ),
                (int(pos[0]) + 10, int(pos[1]))
            )
            if old is not None:
                self.drawmember(old, new)
            if i != len(self.nodes) - 1:
                pos = (Vector(new) + Vector(self.get_coords(self.nodes[i + 1]))) / 2
                dis = (Vector(node) - Vector(self.nodes[i + 1])).size()
                self.screen.blit(
                    font.render(
                        getstats(node.up.size(), dis, COMPRESSION),
                        1, BLACK
                    ),
                    (int(pos[0]) - 40, int(pos[1]))
                )
        if time.time() - self.lastframe < 1.0/60:
            time.sleep(abs(self.lastframe + 1.0/60 - time.time()))
        pygame.display.update()
        self.lastframe = time.time()

    def save(self):
        f = open(self.filename, "w")
        f.write("%f\n%f\n" % (self.height_div, self.width))
        for node in self.nodes[1:]: # avoid saving the zero
            f.write("%f\n" % node.x)
        f.close()

    def quit(self):
        pygame.quit()

class Node(object):
    def __init__(self, x, bridge):
        self.x = x
        self.bridge = bridge
        self.selected = False

    def get_height(self):
        return self.bridge.get_height(self.x)

    def draw(self, screen, index):
        colour = BLUE if self.selected else BLACK
        pygame.draw.circle(screen, colour, self.bridge.get_coords(self), 3, 0)
        font = pygame.font.Font(None, 20)
        text = "%s (%d, %d)" % (ALPHABET[index], self.x, self.get_height())
        x, y = self.bridge.get_coords(self)
        dx, dy = font.size(text)
        text = font.render(text, 1, BLACK)
        if isinstance(self, CentreNode):
            screen.blit(text, (x - dx / 2, y))
        else:
            screen.blit(text, (x - dx, y - dy))
        return (x, y)

class CentreNode(Node):
    def get_height(self):
        return 0

def getstats(force, size, direction):
    if direction == TENSION:
        pressure = force / (math.pi * 1.6e-3 ** 2)
        break_pt = 3.43 / 250 * size
        percent = force / break_pt
        return "%.2f%%" % (percent * 100)
    else:
        pressure = force / (math.pi * (3e-3 ** 2 - 0.75e-3**2))
        break_pt = 0
        percent = 0
        return "%d Pa/mm, %d mm" % (pressure / size, size)

    return "%.2f / %.2fN (%d%%), %dKPa" % (force, break_pt, percent*100, pressure / 1000)

assert not sys.argv[1].endswith(".py")
Bridge(sys.argv[1])
