from jetbot import Robot
import socket
import time

MY_ID = 7

HOST = "127.0.0.1"  # NEED TO WRITE AN ACTUAL IP OF ROBOT
PORT = 8081


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(1)
    print("Server started")
    print("Waiting for client request..")
    clientConnection, clientAddress = server.accept()
    print("Connected clinet :", clientAddress)

    return server, clientConnection


def main():
    robot = Robot()
    print(f"Robot {MY_ID} created")

    server, clientConnection = start_server()

    while True:
        res = clientConnection.recv(1024)

        if not res:
            clientConnection.close()
            break

        result = res.decode('utf-8')
        result = eval(result)

        input_id = int(result["ids"])
        input_left = float(result["left"])
        input_right = float(result["right"])
        input_time = float(result["time"])

        if input_id == MY_ID:
            print(result)

            robot.set_motors(input_left, input_right)
            time.sleep(input_time)
            robot.set_motors(0, 0)
        else:
            pass


if __name__ == '__main__':
    main()
