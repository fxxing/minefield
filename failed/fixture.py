#!/usr/bin/env python
# coding: utf-8

import os
import math
import sys
from PIL import Image

TRANSPARENT_THRESHOLD = 10
ANGLE_THRESHOLD = 0
TRANSPARENT = (255, 255, 255, 0)
BLACK = (0, 0, 0, 255)
VERTEX_COLOR = (0, 255, 0, 255)

# top, top right, right, bottom right, bottom, bottom left, left, top left
ADJANCENCY_DIRECTIONS = ((0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1))


def calc_angle(pt1, pt2):
    x1, y1 = pt1
    x2, y2 = pt2
    inner_product = x1 * x2 + y1 * y2
    len1 = math.hypot(x1, y1)
    len2 = math.hypot(x2, y2)
    return math.acos(inner_product/(len1 * len2))


def near(pt1, pt2, pt3):
    x1, y1 = pt1
    x2, y2 = pt2
    x3, y3 = pt3
    if x1 == x2 == x3 or y1 == y2 == y3:
        return 0
    if x1 != x2:
        m1 = float(y2 - y1) / (x2 - x1)
    else:
        m1 = sys.maxint

    if x2 != x3:
        m2 = float(y3 - y2) / (x3 - x2)
    else:
        m2 = sys.maxint
    if m1 == m2:
        return 0

    if m1 * m2 == -1:
        return 1
    p = float(m2 - m1) / (1 + m1 * m2)
    return abs(math.atan(p))


class FixtureDetecter(object):
    def __init__(self, input_name, output_name, max_vertex):
        super(FixtureDetecter, self).__init__()

        self.input_name = input_name
        self.output_name = output_name
        self.max_vertex = max_vertex
        self.grayscale = None
        self.width = 0
        self.height = 0
        self.vertexs = []

    def detect(self):
        self.calc_grayscale()
        self.dump_grayscale()
        # print self.grayscale[90][84]
        self.find_vertex()
        self.dump_vertex()
        #
        # while 1:
        #     count = self.filter_vertex()
        #     print "delete", count
        #     if len(self.vertexs) < self.max_vertex or count == 0:
        #         break
        # self.dump_vertex()

    def calc_grayscale(self):
        """get the "grayscale" image"""
        im = Image.open(self.input_name)
        self.width, self.height = im.size
        assert self.width > 0
        assert self.height > 0
        self.grayscale = [[0] * self.height for _ in range(self.width)]
        data = list(im.getdata())
        for x in range(self.width):
            for y in range(self.height):
                color = data[y * self.width + x]
                if color[3] >= TRANSPARENT_THRESHOLD:
                    self.grayscale[x][y] = 1
                else:
                    self.grayscale[x][y] = 0

    def filter_vertex(self):
        count = 0
        n = len(self.vertexs)
        i = 1
        while i <= n:
            if i == n - 1:
                prev = self.vertexs[i - 1]
                cur = self.vertexs[i]
                next = self.vertexs[0]
            elif i == n:
                prev = self.vertexs[i - 1]
                cur = self.vertexs[0]
                next = self.vertexs[1]
            else:
                prev = self.vertexs[i - 1]
                cur = self.vertexs[i]
                next = self.vertexs[i + 1]

            angle = near(prev, cur, next)
            if angle <= ANGLE_THRESHOLD:
                self.vertexs.remove(cur)
                n -= 1
                count += 1
            else:
                i += 1
        return count

    def dump_grayscale(self):
        name, ext = os.path.splitext(self.input_name)
        im = Image.new("RGBA", (self.width, self.height), "rgba" + str(TRANSPARENT))
        for x in range(self.width):
            for y in range(self.height):
                if self.grayscale[x][y] == 1:
                    im.putpixel((x, y), BLACK)
        im.save(name + "_grayscale" + ext)

    def dump_vertex(self):
        name, ext = os.path.splitext(self.input_name)
        im = Image.new("RGBA", (self.width, self.height), "rgba" + str(TRANSPARENT))
        for x in range(self.width):
            for y in range(self.height):
                if (x, y) in self.vertexs:
                    im.putpixel((x, y), VERTEX_COLOR)
                elif self.grayscale[x][y]:
                    im.putpixel((x, y), BLACK)
        im.save(name + "_vertex_" + str(len(self.vertexs)) + ext)

    def find_start_vertex(self):
        for x in range(self.width):
            for y in range(self.height):
                if self.grayscale[x][y]:
                    return x, y
        return None

    def find_vertex(self):
        start_point = self.find_start_vertex()
        if not start_point:  # not pixel visible
            return
        vertex = start_point
        while 1:
            print vertex
            self.vertexs.append(vertex)
            vertex = self.find_next_vertex(vertex[0], vertex[1])
            if not vertex:
                break

    def has_adjacency_blank_point(self, x, y):
        for nx, ny in self.get_adjacency_points(x, y):
            if nx < 0 or nx >= self.width or ny < 0 or ny >= self.height or self.grayscale[nx][ny] == 0:
                return True

    def find_next_vertex(self, x, y):
        for nx, ny in self.get_adjacency_points(x, y):
            if nx < 0 or nx >= self.width or ny < 0 or ny >= self.height:
                continue
            if self.grayscale[nx][ny] and self.has_adjacency_blank_point(nx, ny) and (nx, ny) not in self.vertexs:
                return nx, ny
        return None

    def get_adjacency_points(self, x, y):
        for d in ADJANCENCY_DIRECTIONS:
            nx, ny = x + d[0], y + d[1]
            yield nx, ny


if __name__ == "__main__":
    import sys

    input_name = sys.argv[1]
    output_name = sys.argv[2]
    max_vertex = int(sys.argv[3])
    detecter = FixtureDetecter(input_name, output_name, max_vertex)
    detecter.detect()