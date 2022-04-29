# -*- coding: utf-8 -*-

import Camera
import Movement
import random

targets_ids = {
    10: 'Target_#1',
    2: 'Target_#2',
}


class Env:
    def __init__(self):
        self.obstacles = None  # [obs1, obs2, obs3...] - list of obstacles
        self.borders = None  # [x, y, width, height]
        self.targets = []  # Regular list of targets
        self.detectedTargets = None  # List of only detected targets

        """
        :param borders: Contains (x, y) as zero-point and width+height of the polygon
        this list can be count as:
        [
        min_x, 0
        min_y, 1
        max_x, 2
        max_y  3
        ]
        """

    def init_scene(self, capture):
        """
        This function returns the list of scene borders and the list of obstacles

        :param capture: opencv read image from camera
        :return: list(borders), list(obstacles), list(targets)
        """

        _, frame = capture.read()

        self.obstacles = Camera.get_obstacle(capture)

        min_x = int(frame.shape[1] * 0.09)
        min_y = int(10)
        max_x = int(frame.shape[1] * 0.91)
        max_y = int(frame.shape[0] - 10)

        self.borders = [min_x,  # 0
                        max_x,  # 1
                        min_y,  # 2
                        max_y   # 3
                        ]

        # print(f'Polygon borders: {self.borders}')

        targetArucoFound = Camera.findarucomarker(frame)

        if len(targetArucoFound[0]) != 0:
            for bbox, ids in zip(targetArucoFound[0], targetArucoFound[1]):
                if int(ids) in targets_ids:
                    target = Movement.Target(int(ids))
                    target.position = Camera.findArucoCoords(bbox)
                    target.weight = random.random()
                    self.targets.append(target)

        for i in range(len(self.targets)):
            print(f'Targets {self.targets[i].id} position: {self.targets[i].position[4]}')

        return self.borders, self.obstacles, self.targets

    def checkTargets(self):
        """
        This function ask every target for being detected

        :return:
        """
        for target in self.targets:
            if target.isDetected:
                self.detectedTargets.append(target)
