from copy import deepcopy

class Vector():
    def __init__(self, dimensions):
        if str(dimensions.__class__.__name__) in ["Node", "CentreNode"]:
            dimensions = (dimensions.x, dimensions.get_height())
        self.point = dimensions

    def op(self, other, op):
        assert str(other.__class__.__name__) in ["int", "float", "list", "Vector"]
        if isinstance(other, int) or isinstance(other, float):
            other = [other] * len(self.point)
        if isinstance(other, Vector):
            other = other.point
        assert len(self.point) == len(other)
        grouped = [eval("%s%s%s" % (str(float(a)),op,str(float(b)))) for a,b in zip(self.point, other)]
        return Vector(grouped)

    def __add__(self, other):
        return self.op(other, "+")
    def __sub__(self, other):
        return self.op(other, "-")
    def __mul__(self, other):
        return self.op(other, "*")
    def __div__(self, other):
        return self.op(other, "/")
    def __iadd__(self, other):
        self = self + other
    def __isub__(self, other):
        self = self - other
    def __imul__(self, other):
        self = self * other
    def __idiv__(self, other):
        self = self / other

    def sin(self):
        return abs(float(self.point[1]) / self.size())

    def cos(self):
        return abs(float(self.point[0]) / self.size())

    def tan(self):
        return abs(float(self.point[1]) / self.point[0])

    def scale(self, size=1):
        return self / self.size() * size

    def size(self):
        return sum([x**2 for x in self.point]) ** 0.5
    def __getitem__(self, key):
        return self.point[key]
    def __setitem__(self, key, value):
        self.point[key] = value
    def __eq__(self, other):
        assert isinstance(other, Vector)
        return self.point == other.point

    def prod(self, b):
        """Returns the dot product of a and b"""
        return sum((self * b).point)

    def proj(self, b):
        """Returns a vector containing a projected onto b"""
        a = self
        #print a.prod(b) / b.size()
        #print a.prod(b) / (b.size() ** 2)
        return  b * (a.prod(b) / (b.size() ** 2))

    def __str__(self):
        return str(self.point)

    def getobj(self, objects, start = False):
        objects = deepcopy(objects) #deep copy so we don't screw up the old values
        if start:
            for i, obj in enumerate(objects):
                newp = []
                for j, point in enumerate(obj.pos):
                    newp.append(point - start[j])
                objects[i].pos = newp

        dis = []
        for obj in objects:
            center = Vector(obj.pos)
            #print self
            vec = obj.getdis(center, self)
            if vec:
                dis.append((vec.size(), obj.colour, center, vec))

        if not dis:
            return False
        return min(dis)

    def color(self, objects, lights):
        color = self.getobj(objects)
        if not color:
            return False

        ambient = 0.15
        totshade = 0
        #print finalcol
        for light in lights:
            lightToPt = (Vector(light.pos) - color[3]) * -1
            closest = lightToPt.getobj(objects, Vector(light.pos))
            #print lightToPt, lightToPt.size()
            #print closest[3], closest[3].size()
            #print closest[2], closest[2].size()
            #print color[3], color[3].size()
            if closest and closest[3].size() > lightToPt.size() - 1e-6:
                normal = closest[3] - closest[2]
                normal = normal / normal.size()
                #print isinstance(normal, Vector)
                comp = lightToPt / (-lightToPt.size())
                shade = normal.prod(comp) * (1 - ambient)
                if shade < 0:
                    shade = 0
                totshade += shade * light.brightness

        totshade *= 1 - ambient
        totshade += ambient
        out = []
        for group in color[1]:
            out.append(totshade * group)

        return tuple([min(255, int(x)) for x in out])

# if __name__ == "__main__":
    #from shapes import *
    #from scene import Light
    #circle = Sphere([7, 7], 3, (255, 255, 255))
    #light = Light([0, 10])
    #print Vector([4, 7]).color([circle], [light])
