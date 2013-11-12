import sys
import pygame
import string
from vectors import Vector

ALPHABET = string.uppercase + string.lowercase
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Bridge(object):
    def __init__(self, filename):
        try:
            lines = open(filename, "rU").readlines()
        except IOError:
            lines = ["1", "1000"]

        self.filename = filename
        self.height_multi = float(lines[0])
        self.width = float(lines[1])

        self.lowerx = -0.1 * self.width
        self.upperx = 1.1 * self.width
        self.lowery = -0.1 * self.get_height(self.width)
        self.uppery = 1.1 * self.get_height(self.width)

        lines = map(float, ["0"] + lines[2:])
        self.nodes = [Node(x, self) for x in lines]
        self.nodes[0].below = Vector(0, 0.5)

        for i, node in enumerate(self.nodes):
            disp = Vector(node) - Vector(old).scale
            node.up = Vector(
            node.side = self.down * self.down.sin()
            old = node
            after = self.nodes[i + 1]

        self.centre = CentreNode(self.width, self)

        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.close = False

        while not self.close:
            self.update()
            self.draw()
        self.save()
        self.quit()

    def get_height(self, x):
        highest = self.width ** 2
        diff = (self.width - x) ** 2
        return self.height_multi * (highest - diff)

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
                    (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.close = True
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                print event.button

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
        for i, node in enumerate(self.nodes):
            old = new
            new = node.draw(self.screen, i)
            self.drawmember(new, centre)
            if old is not None:
                self.drawmember(old, new)
        pygame.display.update()

    def save(self):
        f = open(self.filename, "w")
        f.write("%f\n%f\n" % (self.height_multi, self.width))
        for node in self.nodes[1:]: # avoid saving the zero
            f.write("%f\n" % node.x)
        f.close()

    def quit(self):
        pygame.quit()

class Node(object):
    def __init__(self, x, bridge):
        self.x = x
        self.bridge = bridge

    def get_height(self):
        return self.bridge.get_height(self.x)

    def draw(self, screen, index):
        pygame.draw.circle(screen, BLACK, self.bridge.get_coords(self), 3, 0)
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


assert not sys.argv[1].endswith(".py")
Bridge(sys.argv[1])
