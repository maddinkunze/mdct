import tkinter as tk
import json
import math
import imageio
import os
import copy
from PIL import Image, ImageTk
from random import random
import numpy as np
from objects3d import Object3D

imageio.plugins.freeimage.download(os.path.abspath(os.curdir))


def hoverCreateFunctions(colorNormal, colorHover):
    def on_hover_enter(event):
        widget = event.widget
        widget.configure(background=colorHover)

    def on_hover_leave(event):
        widget = event.widget
        widget.configure(background=colorNormal)

    return [on_hover_enter, on_hover_leave]


def buttonsCreate(root, names, function=None):
    buttons = {}
    for name in names:
        if function:
            buttons[name] = tk.Button(root, text=name, command=lambda name=name: function(name))
        else:
            buttons[name] = tk.Button(root, text=name)
    return buttons


def colorCodesCreate(root, names):
    ret = {}
    for name in names:
        color = names[name]
        labelColor = tk.Label(root)
        labelColor.configure(background=color)
        labelText = tk.Label(root, text=name)
        ret[labelText] = labelColor
    return ret


def widgetsSetStyle(widgets, style):
    for widget in widgets:
        widget.configure(style)


def widgetsSetHoverFunctions(widgets, functionsHover):
    for widget in widgets:
        widget.bind("<Enter>", functionsHover[0])
        widget.bind("<Leave>", functionsHover[1])


def widgetsPlace(widgets, startX, startY, width, height, margin, orientation="HORIZONTAL"):
    for widget in widgets:
        if width:
            widget.place(x=startX, y=startY, width=width, height=height)
        else:
            widget.place(x=startX, y=startY, height=height)
        if orientation == "HORIZONTAL":
            startX += width + margin
        elif orientation == "VERTICAL":
            startY += height + margin


file = open("templates/template.json")
data = json.load(file)
file.close()


def dataStandardGet():
    return copy.deepcopy(data["example"])


def dataStandardGetEnvironment(name=None):
    if name:
        env = data["standards"]["environments"][name]
    else:
        env = data["standards"]["environments"][list(data["standards"]["environments"])[0]]
    env["settingsScene"] = data["standards"]["settingsScene"]
    return copy.deepcopy(env)


def dataStandardGetEnvironmentNames():
    ret = {}
    for envType in data["types"]["environments"]:
        ret[data["types"]["environments"][envType]["name"]] = envType
    return ret


def dataStandardGetEnvironmentTypes():
    return copy.deepcopy(data["types"]["environments"])


def dataStandardGetObjectTypes(path="objects"):
    return copy.deepcopy(data["types"][path])


def dataStandardGetObjectNames():
    ret = {}
    for objType in data["types"]["objects"]:
        ret[data["types"]["objects"][objType]["name"]] = objType
    return ret


def dataStandardGetObject(path="objects", name=None):
    if not name:
        name = list(data["standards"][path].keys())[0]
    return copy.deepcopy(data["standards"][path][name])


imagesTkinter = {}
images = {}


def getTkinterImageName(path, resize=None):
    if resize:
        return path + " | " + str(resize[0]) + "x" + str(resize[1])
    else:
        return path + " | Original"


def getTkinterImage(path, resize=None, reload=False, mode="FIT"):
    if not os.path.exists(path):
        return None

    if reload:
        for name in imagesTkinter:
            if path in name:
                del imagesTkinter[name]
                imagesTkinter.pop(name)

    name = getTkinterImageName(path, resize)

    if name in imagesTkinter:
        return imagesTkinter[name]
    else:
        if path in images:
            img = images[path]
        else:
            img = imageio.imread(path)
            if img.mean() < 5:
                img = img.clip(0, 1) * 255
            img = img.astype(np.uint8)
            img = Image.fromarray(img)
            images[path] = img
            if resize:
                imagesTkinter[getTkinterImageName(path)] = ImageTk.PhotoImage(img)

        if resize:
            if mode == "FIT":
                aspectImg = img.size[0] / img.size[1]
                aspectResize = resize[0] / resize[1]
                if aspectImg > aspectResize:
                    resize[0] = round(aspectImg * resize[1])
                else:
                    resize[1] = round(1/aspectImg * resize[0])
                img = img.resize(resize)
        tkImg = ImageTk.PhotoImage(img)
        imagesTkinter[name] = tkImg
        return tkImg


def Cart3DToEqui2DOld(pos, size, cam=None):
    if not cam:
        cam = (0, 0, 0)

    x, y, z = pos
    xc, yc, zc = cam
    x, y, z = x-xc, y-yc, z-zc
    w, h = size

    if x == 0:
        x = 0.000001  # Not very beautiful, but to avoid zero divisions
    xs = 0
    if x > 0:
        xs = 1

    r = math.sqrt(x*x + y*y)
    xr = w / 2 * (xs - math.atan(y/x) / math.pi)
    yr = h / 2 * (1 - math.atan(z/r) / (math.pi/2))
    r = math.sqrt(r*r + z*z)

    return xr, yr, r


def normalize(l):
    m = sum([e*e for e in l])
    m = math.sqrt(m)
    if not m:
        return l

    for i in range(len(l)):
        l[i] /= m

    return l


def Cart3DToEqui2D(pos, size, cam=None):
    if not cam:
        cam = (0, 0, 0)

    x, y, z = pos
    xc, yc, zc = cam
    x, y, z = x-xc, y-yc, z-zc
    r = math.sqrt(x*x + y*y + z*z)
    xs, ys = normalize([x, y])
    xn, yn, zn = normalize([x, y, z])
    w, h = size

    relX = 1/4 + math.asin(xs) / (2 * math.pi)
    relY = 1/2 - math.asin(zn) / math.pi

    if y < 0:
        relX = 1 - relX

    xw = w * relX
    yw = h * relY

    return [xw, yw, r]


def getAxisIntersections(p1, p2):
    positions = []

    if p1[0] * p2[0] < 0:
        positions.append((-p1[0])/(p2[0] - p1[0]))
    if p1[1] * p2[1] < 0:
        positions.append((-p1[1])/(p2[1] - p1[1]))
    if p1[2] * p2[2] < 0:
        positions.append((-p1[2])/(p2[2] - p1[2]))

    positions.sort()
    intersections = []

    for p in positions:
        x = p1[0] + (p2[0] - p1[0]) * p
        y = p1[1] + (p2[1] - p1[1]) * p
        z = p1[2] + (p2[2] - p1[2]) * p
        intersections.append([x, y, z])

    return intersections


def drawRect3D(canvas, pos, size, rotation, color="", steps=200, fill="gray50"):
    points = [[+size[0]/2, +size[1]/2, 0], [-size[0]/2, +size[1]/2, 0],
              [-size[0]/2, -size[1]/2, 0], [+size[0]/2, -size[1]/2, 0]]
    obj = Object3D(points, [], [])
    obj = obj.rotateX(rotation[0])
    obj = obj.rotateY(rotation[1])
    obj = obj.rotateZ(rotation[2])

    points3D = []
    for point in obj.points3d:
        points3D.append([point.x + pos[0], point.y + pos[1], point.z + pos[2]])

    drawPoly3D(canvas, points3D, color, steps, fill)


def drawVector3D(canvas, pos, size, rotation, color="", steps=50):
    drawRect3D(canvas, pos, size, rotation, color, steps, "")
    drawLine3D(canvas, pos, math.sqrt(size[0]**2 + size[1]**2), rotation, color, steps)


def drawLine3D(canvas, pos, size, rotation, color="", steps=50):
    points = [[0, 0, 0], [0, 0, size]]
    obj = Object3D(points, [], [])
    obj = obj.rotateX(rotation[0])
    obj = obj.rotateY(rotation[1])
    obj = obj.rotateZ(rotation[2])

    points3D = []
    for point in obj.points3d:
        points3D.append([point.x + pos[0], point.y + pos[1], point.z + pos[2]])

    drawPoly3D(canvas, points3D, color, steps, "")


def drawCircle3D(canvas, pos, size, color, steps=50, fill="gray25"):
    d = math.sqrt(pos[0]**2 + pos[1]**2 + pos[2]**2)
    if not d: return
    points = []
    for angle in range(0, 360, 5):
        a = math.radians(angle)
        points.append([0, math.sin(a)*size/2, math.cos(a)*size/2])

    ax = math.acos(pos[0]/d)
    ay = math.acos(pos[1]/d)
    # az = math.acos(pos[2]/d)

    p2 = math.pi/2

    obj = Object3D(points, [], [])
    # obj = obj.rotateX(p2-az)
    if pos[2] > 0:
        ax *= -1
    obj = obj.rotateY(ax)
    obj = obj.rotateZ(p2-ay)  # Not perfect at all, but it works somehow, i guess

    points = []
    for point in obj.points3d:
        points.append([point.x + pos[0], point.y + pos[1], point.z + pos[2]])

    drawPoly3D(canvas, points, color, steps, fill)


def drawPoly3D(canvas, points, color="", steps=200, fill="gray50"):
    points2D = []
    extend = False

    canExtend = False
    xp, xn, yp, yn = [False] * 4
    for e in range(len(points)):
        p1 = points[e - 1]
        p2 = points[e]
        for i in getAxisIntersections(p1, p2):
            if i[0] == 0:
                if i[1] >= 0:
                    yp = True
                else:
                    yn = True
            elif i[1] == 0:
                if i[0] >= 0:
                    xp = True
                else:
                    xn = True

    if xp and xn and yp and yn:
        canExtend = True

    p = x, y, z = 0, 0, 0
    w, h = canvas.winfo_width(), canvas.winfo_height()
    for e in range(len(points)):
        p1 = points[e-1]
        p2 = points[e]
        lx, ly, lz = p1
        lp = Cart3DToEqui2D((lx, ly, lz), (w, h))
        for i in range(steps):
            x = p1[0] + (p2[0] - p1[0]) * (i / steps)
            y = p1[1] + (p2[1] - p1[1]) * (i / steps)
            z = p1[2] + (p2[2] - p1[2]) * (i / steps)
            p = Cart3DToEqui2D((x, y, z), (w, h))

            if not ((x <= 0) and (lx <= 0) and (((ly <= 0) and (y >= 0)) or ((ly >= 0) and (y <= 0)))):
                canvas.create_line(lp[0], lp[1], p[0], p[1], fill=color)
            else:
                if canExtend:
                    relY = 0
                    if z < 0:
                        relY = 1
                    elif z > 0:
                        relY = -1
                    points2D.append(lp[0])
                    points2D.append(lp[1] + relY * h)
                    points2D.append(points2D[0])
                    points2D.append(points2D[1] + relY * h)
                    extend = True
                elif points2D:
                    points2D.append(lp[0])
                    points2D.append(points2D[1])
                if fill:
                    canvas.create_polygon(*points2D, width=2, fill=color, stipple=fill)
                points2D = []

            points2D.append(p[0])
            points2D.append(p[1])
            lp = p
            lx, ly, lz = x, y, z

    if extend:
        relY = 0
        if z < 0:
            relY = 1
        elif z > 0:
            relY = -1
        points2D.append(p[0])
        points2D.append(p[1] + relY * h)
        points2D.append(points2D[0])
        points2D.append(points2D[1] + relY * h)
    else:
        points2D.append(points2D[0])
        points2D.append(points2D[-2])
    if fill:
        canvas.create_polygon(*points2D, width=2, fill=color, stipple=fill)


def evalDriver(expression, variables=None):
    def rand(_self, _frame):
        return random()
    stdVars = {"label": 0, "pi": math.pi, "frame": 0, "random": rand, "self": None}
    # TODO: here should go some input check to avoid breaks
    return eval(expression, stdVars, variables)


def getFromObj(obj, objTypeId, objType, key, num=0):
    ret = obj.get(key, None)
    if ret is None:
        if objType.get(key) is not None:
            if num:
                ret = [objType[key].get("default", "0")] * num
            else:
                ret = objType[key].get("default", "0")
        else:
            if num:
                ret = data["standards"][objTypeId][obj["type"]].get(key, ["0"] * num)
            else:
                ret = data["standards"][objTypeId][obj["type"]].get(key, ["0"])
    return ret


def getEvalFromObj(obj, objTypeId, objType, key, num=0):
    fromObj = getFromObj(obj, objTypeId, objType, key, num)
    if num:
        return [evalDriver(e) for e in fromObj]
    else:
        return evalDriver(fromObj)
