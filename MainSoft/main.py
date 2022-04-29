# -*- coding: utf-8 -*-

import Camera
import Movement
import time
import Environment
import Communication

import cv2


def index_getting(massive, ids):
    for i in range(len(massive)):
        if massive[i].id == ids:
            return i


def main():
    print('im in')
    # STEP-1: GET THE DATA FROM CAMERAS
    cap = Camera.getAllCameraImages()

    cap = cap[3]  # REQUIRES CORRECTION

    # STEP-2: FIND TARGETS AND OBSTACLES
    env = Environment.Env()

    env.init_scene(cap)

    currentTime = 0  # REQUIRES CORRECTION

    # STEP-3: FORMING THE SWARM AND COMMAND-OBJECT
    swarm = Movement.Swarm()
    print(swarm.RobotIDs)

    # STEP-4: START THE SHOW
    while True:
        # LET'S GET THE IMAGE AND CALL IT FRAME
        success, frame = cap.read()

        if not success:
            break

        cadr = Camera.cropImage(frame, env.borders[2], env.borders[3], env.borders[0], env.borders[1])

        cadr = Camera.rescaleFrame(cadr, 75)

        cv2.imshow('Video', cadr)

        # FIND ALL ARUCO-MARKER ON FRAME
        arucoFound = Camera.findarucomarker(frame)

        # HERE DEFINE THE GOAL
        try:
            swarm.define_goal(env)
        except Exception as e:
            print(str(e))
            pass

        # CHECK FOUNDED ARUCO-MARKERS
        if len(arucoFound[0]) != 0:

            # COME THROUGH DIVIDING BY COORDS AND IDs
            for bbox, ids in zip(arucoFound[0], arucoFound[1]):

                # CHECK IF THIS MARKER IS ROBOT
                if int(ids) in swarm.RobotIDs:

                    # FIND THE INDEX OF THIS ROBOT IN ROBOT'S-LIST
                    index = index_getting(swarm.RobotList, int(ids))
                    robot = swarm.RobotList[index]
                    print(f'Robot {robot.id} is found')

                    # REFER TO SPECIFIC ROBOT TO GET HIS COORDINATES MORE DETAILING
                    robot.position = Camera.findArucoCoords(bbox)
                    print(f'Robot position: {robot.position[4]}')

                    print(f'Goal reached? {robot.goalReached}')
                    print(f'Robot {robot.id} Goal: {robot.goal}')

                    # FIND ORIENTATION OF ROBOT TO GOAL
                    try:
                        robot.orientation = robot.get_orientation(robot.goal)
                        print(f'Robot {robot.id} angle: {robot.orientation[0]}, dist: {robot.orientation[1]}')

                        Movement.MeineRobot.set_wheels(robot)
                    except Exception as e:
                        print(str(e))
                        continue

                    try:
                        Communication.send_message(robot.id, robot.left_wheel, robot.right_wheel, robot.exec_time)
                    except Exception as e:
                        print(str(e))

                    # if round(time.time() * 1000) - currentTime > 500:
                    #     ids = robot.id
                    #     left = robot.left_wheel
                    #     right = robot.right_wheel
                    #     exec_time = robot.exec_time
                    #
                    #     Communication.send_message(ids, left, right, exec_time)
                    #
                    #     currentTime = round(time.time() * 1000)

                #######################################################################
                # NOW WE'VE GOT THESE PROBLEMS:
                # 1. ROBOTS CAN BUMP EACH OTHER
                # 2. SOME ROBOTS ARE FASTER THAN OTHERS, NEED WAIT EACH OTHER
                #######################################################################

                if int(ids) in env.targets:
                    pass
        else:
            print('Метки не обнаружены')

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()


if __name__ == '__main__':
    main()
