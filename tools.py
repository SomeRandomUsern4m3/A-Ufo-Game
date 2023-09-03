import math
def center_image(image, anchor_x="center", anchor_y="center"):
    timage = image #copy of the image
    match anchor_x:
        case "left":
            print("not err")
        case "center":
            timage.anchor_x = timage.width//2
        case "right":
            timage.anchor_x = timage.width
        case _:
            timage.anchor_x = timage.width//2
    match anchor_y:
        case "bottom":
            print("not err")
        case "center":
            timage.anchor_y = timage.height//2
        case "top":
            timage.anchor_y = timage.height
        case _:
            timage.anchor_y = timage.height//2
    return timage
def CheckAABBCollision(one, two):
    collisionX = one.x + one.width >= two.x and two.x + two.width >= one.x
    collisionY = one.y + one.height >= two.y and two.y + two.height >= one.y
    return collisionX and collisionY
def remove_at(i, s):
    return s[:i] + s[i+1:]
def getRect(rec, anchor_x="center", anchor_y="center"):
    """
    Returns the four scaled\rotated rect points in clockwise order :
    lt, rt, rb, lb
    """
    match anchor_x:
        case "left":
            left = rec.x
            right = rec.x + rec.width
        case "center":
            left = rec.x - rec.width//2
            right = rec.x + rec.width//2
        case "right":
            left = rec.x - rec.width
            right = rec.x
        case _:
            pass
    match anchor_y:
        case "top":
            top = rec.y
            bottom = rec.y - rec.height
        case "center":
            top = rec.y + rec.height//2
            bottom = rec.y - rec.height//2
        case "bottom":
            top = rec.y + rec.height
            bottom = rec.y
        case _:
            pass

    lt = (left,top)
    rt = (right,top)
    lb = (left,bottom)
    rb = (right,bottom)

    # Get rotated positions:
    if  rec.rotation:
        # Note, as seen below, each of the y's in the first column to the left
        # are subtracted, rather than added like their 'x' counterpart.  I'm
        # not sure why this is needed, but it's very bad if you don't.
        ltx = rec.x + ((lt[0]-rec.x)*math.cos(math.radians(rec.rotation)) - \
                        (lt[1]-rec.y)*math.sin(math.radians(rec.rotation)))
        lty = rec.y - ((lt[0]-rec.x)*math.sin(math.radians(rec.rotation)) + \
                        (lt[1]-rec.y)*math.cos(math.radians(rec.rotation)))
        lt = (ltx, lty)

        rtx = rec.x + ((rt[0]-rec.x)*math.cos(math.radians(rec.rotation)) - \
                        (rt[1]-rec.y)*math.sin(math.radians(rec.rotation)))
        rty = rec.y - ((rt[0]-rec.x)*math.sin(math.radians(rec.rotation)) + \
                        (rt[1]-rec.y)*math.cos(math.radians(rec.rotation)))
        rt = (rtx, rty)

        rbx = rec.x + ((rb[0]-rec.x)*math.cos(math.radians(rec.rotation)) - \
                        (rb[1]-rec.y)*math.sin(math.radians(rec.rotation)))
        rby = rec.y - ((rb[0]-rec.x)*math.sin(math.radians(rec.rotation)) + \
                        (rb[1]-rec.y)*math.cos(math.radians(rec.rotation)))
        rb = (rbx, rby)

        lbx = rec.x + ((lb[0]-rec.x)*math.cos(math.radians(rec.rotation)) - \
                        (lb[1]-rec.y)*math.sin(math.radians(rec.rotation)))
        lby = rec.y - ((lb[0]-rec.x)*math.sin(math.radians(rec.rotation)) + \
                        (lb[1]-rec.y)*math.cos(math.radians(rec.rotation)))
        lb = (lbx, lby)

    return lt, rt, rb, lb
def normalize(vector):
    """
    :return: The vector scaled to a length of 1
    """
    norm = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
    return vector[0] / norm, vector[1] / norm


def dot(vector1, vector2):
    """
    :return: The dot (or scalar) product of the two vectors
    """
    return vector1[0] * vector2[0] + vector1[1] * vector2[1]


def edge_direction(point0, point1):
    """
    :return: A vector going from point0 to point1
    """
    return point1[0] - point0[0], point1[1] - point0[1]


def orthogonal(vector):
    """
    :return: A new vector which is orthogonal to the given vector
    """
    return vector[1], -vector[0]


def vertices_to_edges(vertices):
    """
    :return: A list of the edges of the vertices as vectors
    """
    return [edge_direction(vertices[i], vertices[(i + 1) % len(vertices)])
            for i in range(len(vertices))]


def project(vertices, axis):
    """
    :return: A vector showing how much of the vertices lies along the axis
    """
    dots = [dot(vertex, axis) for vertex in vertices]
    return [min(dots), max(dots)]


def overlap(projection1, projection2):
    """
    :return: Boolean indicating if the two projections overlap
    """
    return min(projection1) <= max(projection2) and \
           min(projection2) <= max(projection1)


def separating_axis_theorem(vertices_a, vertices_b):
    edges = vertices_to_edges(vertices_a) + vertices_to_edges(vertices_b)
    axes = [normalize(orthogonal(edge)) for edge in edges]

    for axis in axes:
        projection_a = project(vertices_a, axis)
        projection_b = project(vertices_b, axis)

        overlapping = overlap(projection_a, projection_b)

        if not overlapping:
            return False

    return True

