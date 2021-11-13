import math


# class Point3D published by "lefam" on http://codentronix.com/2011/04/21/rotating-3d-wireframe-cube-with-python/
# The scale and move functions were added and the project function was rewritten afterwards by Martin Kunze
class Point3D:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x, self.y, self.z = float(x), float(y), float(z)

    def rotateX(self, angle):
        """ Rotates the point around the X axis by the given angle in degrees. """
        # rad = angle * math.pi / 180
        rad = angle
        cosa = math.cos(rad)
        sina = math.sin(rad)
        y = self.y * cosa - self.z * sina
        z = self.y * sina + self.z * cosa
        return Point3D(self.x, y, z)

    def rotateY(self, angle):
        """ Rotates the point around the Y axis by the given angle in degrees. """
        # rad = angle * math.pi / 180
        rad = angle
        cosa = math.cos(rad)
        sina = math.sin(rad)
        z = self.z * cosa - self.x * sina
        x = self.z * sina + self.x * cosa
        return Point3D(x, self.y, z)

    def rotateZ(self, angle):
        """ Rotates the point around the Z axis by the given angle in rad. """
        # rad = angle * math.pi / 180
        rad = angle
        cosa = math.cos(rad)
        sina = math.sin(rad)
        x = self.x * cosa - self.y * sina
        y = self.x * sina + self.y * cosa
        return Point3D(x, y, self.z)

    def scaleX(self, scale):
        x = self.x * scale
        return Point3D(x, self.y, self.z)

    def scaleY(self, scale):
        y = self.y * scale
        return Point3D(self.x, y, self.z)

    def scaleZ(self, scale):
        z = self.z * scale
        return Point3D(self.x, self.y, z)

    def moveX(self, amount):
        x = self.x + amount
        return Point3D(x, self.y, self.z)

    def moveY(self, amount):
        y = self.y + amount
        return Point3D(self.x, y, self.z)

    def moveZ(self, amount):
        z = self.z + amount
        return Point3D(self.x, self.y, z)

    def project(self, win_width, win_height, angle_of_view, viewer_distance):
        """ Transforms this 3D point to 2D using a perspective projection. """
        # fov = win_width / 90 * angle
        # factor = fov / (viewer_distance + self.z)
        # x = self.x * factor + win_width / 2
        # y = -self.y * factor + win_height / 2
        if self.z + viewer_distance:
            wx = math.atan(self.x / (self.z + viewer_distance)) * 180 / math.pi
            wy = math.atan(self.y / (self.z + viewer_distance)) * 180 / math.pi
        else:
            if self.x > 0: wx = 90
            else: wx = -90
            if self.y > 0: wy = 90
            else: wy = -90

        aow_x = angle_of_view
        aow_y = angle_of_view * (win_height / win_width)

        x = (wx + aow_x/2) / aow_x * win_width
        y = (wy + aow_y/2) / aow_y * win_height

        return Point3D(x, y, 1)


class Object3D:
    def __init__(self, vertices, edges, faces):
        self.vertices = vertices
        self.edges = edges
        self.faces = faces

        self.points3d = []
        self._update_vertices()

    def _update_vertices(self):
        self.points3d = []
        for vertex in self.vertices:
            if isinstance(vertex, Point3D):
                self.points3d.append(vertex)
            else:
                x, y, z  = vertex
                self.points3d.append(Point3D(x, y, z))

    def rotateX(self, angle):
        points = []
        for point in self.points3d:
            points.append(point.rotateX(angle))
        return Object3D(points, self.edges, self.faces)

    def rotateY(self, angle):
        points = []
        for point in self.points3d:
            points.append(point.rotateY(angle))
        return Object3D(points, self.edges, self.faces)

    def rotateZ(self, angle):
        points = []
        for point in self.points3d:
            points.append(point.rotateZ(angle))
        return Object3D(points, self.edges, self.faces)

    def scaleX(self, scale):
        points = []
        for point in self.points3d:
            points.append(point.scaleX(scale))
        return Object3D(points, self.edges, self.faces)

    def scaleY(self, scale):
        points = []
        for point in self.points3d:
            points.append(point.scaleY(scale))
        return Object3D(points, self.edges, self.faces)

    def scaleZ(self, scale):
        points = []
        for point in self.points3d:
            points.append(point.scaleZ(scale))
        return Object3D(points, self.edges, self.faces)

    def moveX(self, amount):
        points = []
        for point in self.points3d:
            points.append(point.moveX(amount))
        return Object3D(points, self.edges, self.faces)

    def moveY(self, amount):
        points = []
        for point in self.points3d:
            points.append(point.moveY(amount))
        return Object3D(points, self.edges, self.faces)

    def moveZ(self, amount):
        points = []
        for point in self.points3d:
            points.append(point.moveZ(amount))
        return Object3D(points, self.edges, self.faces)

    def copy(self):
        return Object3D(self.points3d, self.edges, self.faces)
