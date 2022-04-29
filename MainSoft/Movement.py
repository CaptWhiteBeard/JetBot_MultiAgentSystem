# -*- coding: utf-8 -*-

import Camera
import random
from math import pi

robot_ids = {
    # 1: 'Robot_#1',
    7: 'Robot_#7',
    5: 'Robot_#5'
}


class MeineRobot:
    HOST = "192.168.0.187"  # Standard loopback interface address (localhost)
    PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

    def __init__(self, id):
        self.id = id
        self.signal = True
        self.left_wheel = 0
        self.right_wheel = 0
        self.exec_time = 0.1  # Time of execution the action

        self.position = None  # [topl, topr, botl, botr, center, mid_top, mid_bot, mid_left, mid_right]
        self.orientation = None  # [angle_delta, dist_to_goal]
        self.angle_delta = None
        self.dist_to_goal = None

        self.best_distance = 1000

        self.goal = None
        self.goalReached = False
        self.endpoint = 120
        self.endofscript = False

        self.speed = 0.4  # Power of signal to the motor. Signal [-1; 1] - depends on rotation direction
        self.stop = False  # Robot stops until True

        self.dx = random.randint(10, 25)
        self.dy = random.randint(10, 25)

        self.cp = 0.5
        self.cg = 0.5
        self.Ac = 0.5
        self.rp = 0.5
        self.rg = 0.5

        self.Vitx = None
        self.Vity = None

        self.local_best = None  # Для первого шага локальное лучшее - координаты установки точки

        self.pole = 30

        self.BotConn = -1
        self.BotAdress = -1
        self.signal = None

    def get_orientation(self, target_position):

        self.orientation = Camera.calc_orientation(self.position, target_position)
        self.angle_delta = self.orientation[0]
        self.dist_to_goal = self.orientation[1]

        return self.orientation

    def set_wheels(self):
        if self.stop == False:
            if self.dist_to_goal < self.endpoint:
                self.left_wheel = 0
                self.right_wheel = 0
                self.goalReached = True
                self.stop = True
            elif self.angle_delta > 0.3 and abs(self.angle_delta - 2 * pi) > 0.3:
                if self.angle_delta < pi:
                    self.left_wheel = -self.speed
                    self.right_wheel = self.speed
                    self.exec_time = 0.1
                else:
                    self.left_wheel = self.speed
                    self.right_wheel = -self.speed
                    self.exec_time = 0.1
            else:
                self.left_wheel = self.speed
                self.right_wheel = self.speed
                self.exec_time = 0.2
        else:
            self.speed = 0
            self.left_wheel = self.speed
            self.right_wheel = self.speed

    def get_random_point(self, env):

        new_random_point = []

        # new_random_point[0] = self.position[4][0] + self.dx
        x = self.position[4][0] + self.dx
        new_random_point.append(x)
        if self.position[4][0] >= env.borders[2] or self.position[4][0] <= env.borders[0]:
            self.dx = -self.dx

        # new_random_point[1] = self.position[4][1] + self.dy

        y = self.position[4][1] + self.dy
        new_random_point.append(y)

        if self.position[4][1] >= env.borders[3] or self.position[4][1] <= env.borders[1]:
            self.dy = -self.dy

        return new_random_point

    def get_PSO_point(self, swarm):

        new_PSO_point = []

        if self.Vitx is None and self.Vity is None:
            self.Vitx = self.dx
            self.Vity = self.dy

        """
        Vit = Ac * Vi-1 + Cp * Rp * (local_best - position) + Сg * Rg * (global_best - position)
        """

        self.Vitx = self.Ac * self.dx \
                    + self.cp * self.rp * (self.local_best[0] - self.position[0]) \
                    + self.cg * self.rg * (swarm.best_position[0] - self.position[0])

        self.Vity = self.Ac * self.dy \
                    + self.cp * self.rp * (self.local_best[1] - self.position[1]) \
                    + self.cg * self.rg * (swarm.best_position[1] - self.position[1])

        new_PSO_point[0] = (self.Vitx, self.Vity)

        return new_PSO_point

    def detectTarget(self, target):
        pass

    def get_new_local_best(self, target):
        pass


class Target:
    def __init__(self, id):
        self.id = id
        self.position = ()
        self.isDetected = False
        self.isDestroyed = False
        self.weight = 0.5
        self.pole = 150


class Swarm:
    def __init__(self):
        self.RobotList = []
        self.best_position = None
        self.global_best_distance = 1000
        self.foundGoals = []
        self.RobotIDs = []

        for id in robot_ids:
            robot = MeineRobot(id)
            self.RobotList.append(robot)
            self.RobotIDs.append(id)

    def check_destination(self):
        counter = 0
        for robot in self.RobotList:
            if robot.goalReached == True:
                counter += 1
            elif robot.goalReached == False:
                counter = 0
        return counter

    def define_goal(self, env):

        FIRST_GOAL = [env.borders[0] + 200, env.borders[2] + 200]
        SECOND_GOAL = [env.borders[0] + 100, env.borders[3] - 200]
        THIRD_GOAL = [env.borders[1] - 200, env.borders[2] + 100]
        FOURTH_GOAL = [env.borders[1] // 2, env.borders[3] // 2]

        FIFTH_GOAL = env.targets[0].position[4]
        SIXTH_GOAL = env.targets[1].position[4]

        # MOVING BETWEEN TARGETS
        #
        # for robot in self.RobotList:
        #     if robot.goal is None:
        #         robot.goal = env.targets[0].position[4]
        #     if robot.goalReached and robot.goal == env.targets[1].position[4]:
        #         robot.goal = env.targets[0].position[4]
        #         robot.goalReached = False
        #         robot.stop = False
        #     elif robot.goalReached and robot.goal == env.targets[0].position[4]:
        #         robot.goal = env.targets[1].position[4]
        #         robot.goalReached = False
        #         robot.stop = False
        checker = bool(self.check_destination())

        for robot in self.RobotList:
            if robot == self.RobotList[0]:
                if robot.goal is None:
                    robot.goal = FIRST_GOAL
                    robot.goalReached = False
                    robot.stop = False
                if robot.goalReached and checker and robot.goal == FIRST_GOAL:
                    robot.goal = SECOND_GOAL
                    robot.goalReached = False
                    robot.stop = False
            else:
                if robot.goal is None:
                    robot.goal = self.RobotList[self.RobotList.index(robot) - 1].position[4]
                if not self.RobotList[0].endofscript:
                    robot.goal = self.RobotList[self.RobotList.index(robot) - 1].position[4]
                    robot.endpoint = 150
                if self.RobotList[0].endofscript:
                    robot.endpoint = 120
                    robot.goal = SIXTH_GOAL

        # for robot in self.RobotList:
        #     if robot == self.RobotList[0]:
        #         if robot.goal is None:
        #             robot.goal = FIRST_GOAL
        #             robot.goalReached = False
        #             robot.stop = False
        #         if robot.goalReached and robot.goal == FIRST_GOAL:
        #             robot.goal = SECOND_GOAL
        #             robot.goalReached = False
        #             robot.stop = False
        #         # if robot.goalReached and robot.goal == SECOND_GOAL:
        #         #     robot.goal = THIRD_GOAL
        #         #     robot.goalReached = False
        #         #     robot.stop = False
        #         if robot.goalReached and robot.goal == SECOND_GOAL:
        #             robot.goal = THIRD_GOAL
        #             robot.goalReached = False
        #             robot.stop = False
        #         # if robot.goalReached and robot.goal == THIRD_GOAL:
        #         #     robot.goal = FOURTH_GOAL
        #         #     robot.goalReached = False
        #         #     robot.stop = False
        #         # if robot.goalReached and robot.goal == FOURTH_GOAL:
        #         #     robot.goal = FIFTH_GOAL
        #         #     robot.goalReached = False
        #         #     robot.stop = False
        #         if robot.goalReached and robot.goal == THIRD_GOAL:
        #             robot.goal = FIFTH_GOAL
        #             robot.goalReached = False
        #             robot.stop = False
        #         if robot.goalReached:
        #             robot.endofscript = True
        #             robot.stop = True
        #     else:
        #         if robot.goal is None:
        #             robot.goal = self.RobotList[self.RobotList.index(robot) - 1].position[4]
        #         if not self.RobotList[0].endofscript:
        #             robot.goal = self.RobotList[self.RobotList.index(robot) - 1].position[4]
        #             robot.endpoint = 150
        #         if self.RobotList[0].endofscript:
        #             robot.endpoint = 120
        #             robot.goal = SIXTH_GOAL

    def new_global_best(self):
        for robot in self.RobotList:
            if robot.best_distance < self.global_best_distance:
                self.global_best_distance = robot.best_distance
                self.best_position = robot.position
