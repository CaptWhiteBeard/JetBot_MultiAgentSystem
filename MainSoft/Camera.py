# -*- coding: utf-8 -*-

import numpy as np
import cv2
import cv2.aruco as aruco
import os
import matplotlib.pyplot as plt
from math import atan2, sqrt, degrees, radians

# Полигон имеет 4 камеры и изначально планировалось использовать их все. На данном этапе используется только одна - 94ая.

# The landfill has four cameras and was originally planned to use them all. At this stage, only one is in use - the 94th.

cameras_dict = {
    1: "http://admin:admin@192.168.0.91:8008",
    2: "http://admin:admin@192.168.0.92:8008",
    3: "http://admin:admin@192.168.0.93:8008",
    4: "http://admin:admin@192.168.0.94:8008",
    5: 0}


# Как следует из названия - поиск АрУко-маркеров. Возвращает координаты углов каждого маркера. Координатная плоскость - само изображение.

# As the name implies, the search for ArUco markers. Returns the coordinates of the corners of each marker. The coordinate plane is the image itself. 

def findarucomarker(img, markersize=4, totalmarker=250, draw=True):
    """
    This function let you get aruco-markers' coordinates

    :param img: the image where search is performed
    :param markersize: size of marker
    :param totalmarker: size of markers' dictionary
    :param draw: bool - Whether to draw
    :return: list of coordinates and ids
    """
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # key = getattr(aruco, f'DICT_{markersize}X{markersize}_{totalmarker}')
    key = getattr(aruco, 'DICT_4X4_250')
    arucoDict = aruco.Dictionary_get(key)
    arucoParam = aruco.DetectorParameters_create()

    bbox, ids, rejected = aruco.detectMarkers(imgGray, arucoDict, parameters=arucoParam)

    # print(ids)
    # print(bbox)

    if draw:
        aruco.drawDetectedMarkers(img, bbox)

    return [bbox, ids]


# Специальная функция для подсчёта остальных важных точек АрУко-маркера

# Special function for calculating the remaining important points of the ArUko Marker

def findArucoCoords(bbox):
    """
    This function return the list of every point of Aruco-marker

    :param bbox: the list of coordinates of only one aruco-marker
    :return: list with every important point of the marker
    """
    topl = bbox[0][0][0], bbox[0][0][1]
    botl = bbox[0][3][0], bbox[0][3][1]
    topr = bbox[0][1][0], bbox[0][1][1]
    botr = bbox[0][2][0], bbox[0][2][1]

    center = ((topl[0] + botr[0]) // 2,
              (topl[1] + botr[1]) // 2)

    mid_top = ((topl[0] + topr[0]) // 2, (topl[1] + topr[1]) // 2)
    mid_bot = ((botl[0] + botr[0]) // 2, (botl[1] + botr[1]) // 2)
    mid_left = ((topl[0] + botl[0]) // 2, (topl[1] + botl[1]) // 2)
    mid_right = ((topr[0] + botr[0]) // 2, (topr[1] + botr[1]) // 2)

    coords = [topl,  # 0
              topr,  # 1
              botl,  # 2
              botr,  # 3
              center,  # 4
              mid_top,  # 5
              mid_bot,  # 6
              mid_left,  # 7
              mid_right]  # 8

    return coords

# Функция для вычисления ориентации объекта к цели. Возвращает угол и расстояние до цели.

# Function for calculating the orientation of an object to a target. Returns the angle and distance to the target.

def calc_orientation(coords, target):
    """
    This function calculate the orientation of mobile robot

    :param coords: Coordinates of mobile robot through Aruco-marker
    :param target: The point where the robot should move
    :return: list of orientation parameters
    """

    angle_delta = angle_between_three(coords[5], coords[4], target)

    dist_to_goal = sqrt(
        ((coords[4][0] - target[0]) ** 2) + ((coords[4][1] - target[1]) ** 2))

    calculations = [
        angle_delta,  # 0
        dist_to_goal  # 1
    ]

    return calculations

# Вычисление угла от объекта до цели по трём точкам: центр АрУко-маркера, центр фронтальной части АрУко-маркера и центр цели.

# Calculation of the angle from object to target using three points: the center of the ArUco marker, 
# the center of the front of the ArUco marker, and the center of the target.

def angle_between_three(p1, p2, p3):
    """
    :param p1: some point (x, y)
    :param p2: angle center point (x, y)
    :param p3: some point (x, y)
    :return: angle in radians, positive, anti-clockwise
    """
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    deg1 = (360 + degrees(atan2(x1 - x2, y1 - y2))) % 360
    deg2 = (360 + degrees(atan2(x3 - x2, y3 - y2))) % 360
    return radians(deg2 - deg1) if deg1 <= deg2 else radians(360 - (deg1 - deg2))

# Функция для поиска препятствий по изображению. Препятствия представляют собой бумажный параллелепипед.

# Function for finding obstacles on the image. Obstacles are paper parallelepipeds.

def find_obstacle(img):
    """
    This function finds obstacles on image

    :param img: Source image where obstacles are
    :return: list of obstacles coordinates
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    gray = cv2.GaussianBlur(gray, (5, 5), 3)

    canny = cv2.Canny(gray, 125, 175)

    countours, hierarchies = cv2.findContours(canny, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    rects = []

    # In our project obstacles are like white paper cubes so important only their sizes in pixels

    for i in countours:
        rect = cv2.boundingRect(i)

        x, y, w, h = rect
        if 255 < x < 1370 and 38 < y < 800:
            if 90 < w < 200 and 90 < h < 200:
                # cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                rects.append(rect)

    return rects

# Функция для определения положения препятствий. Препятствия статичны. 

# Function for determining the position of obstacles. Obstacles are static. 

def get_obstacle(capture):
    """
    This function needs to get obstacles from first frame of video

    :param capture: captured image from camera
    :return: list of obstacles coordinates
    """
    _, frame = capture.read()

    obstacles = find_obstacle(frame)

    return obstacles

# Функция для получения изображения сразу со всех камер

# Function for acquiring images from all cameras at once

def getAllCameraImages():
    cap1 = cv2.VideoCapture(cameras_dict[1])
    cap2 = cv2.VideoCapture(cameras_dict[2])
    cap3 = cv2.VideoCapture(cameras_dict[3])
    cap4 = cv2.VideoCapture(cameras_dict[4])

    return [cap1,  # 0
            cap2,  # 1
            cap3,  # 2
            cap4   # 3
            ]

# Так как на изображении присутствуют элементы, которые находятся вне рабочего полигона, их следует обрезать.  

# Since there are elements on the image that are outside the working polygon, they should be cropped. 

def cropImage(frame, min_x, max_x, min_y, max_y):
    croped_image = frame[min_x:max_x, min_y:max_y]
    return croped_image

# Чтобы можно было удобнее наблюдать за полученным изображением, которое выводится на экран, его необходимо уменьшить. 

# To be able to observe the resulting image displayed on the screen more conveniently, it should be reduced. 

def rescaleFrame(frame, scale=0.75):
    # Images, Videos and Live videos

    scale_percent = scale  # percent of original size
    width = int(frame.shape[1] * scale_percent / 100)
    height = int(frame.shape[0] * scale_percent / 100)
    dim = (width, height)

    # resize image
    resized = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

    return resized
