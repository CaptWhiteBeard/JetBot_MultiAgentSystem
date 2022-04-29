import socket

message = {}

robot_ids = {
    # 1: 'Robot_#1',
    7: '192.168.0.117',
    5: '192.168.0.122'
}

SERVER_1 = "127.0.0.1"
PORT_1 = 8081

SERVER_2 = "127.0.0.1"
PORT_2 = 8082

SERVER_3 = "127.0.0.1"
PORT_3 = 8083

CLIENTS_LIST = []
SERVER_LIST = [(SERVER_1, PORT_1), (SERVER_2, PORT_2), (SERVER_3, PORT_3)]
CHECK_CONNECTION = []
CONTROL_LIST = [False] * len(SERVER_LIST)


def connection():
    global CLIENTS_LIST

    for address in SERVER_LIST:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(address)
            CLIENTS_LIST.append(client)
            CHECK_CONNECTION.append(True)
            client.sendall(bytes(f"Connection {SERVER_LIST.index(address) + 1} Done", 'UTF-8'))
        except Exception as e:
            print(str(e))
            continue

    if CHECK_CONNECTION == CONTROL_LIST:
        for client in CLIENTS_LIST:
            client.close()


def send_message(ids, left_wheel, right_wheel, exec_time):
    global CLIENTS_LIST, message

    message = {'ids': ids,
               'left_wheel': left_wheel,
               'right_wheel': right_wheel,
               'execution_time': exec_time}
    message = str(message)

    for client in CLIENTS_LIST:
        client.sendall(bytes(message, 'UTF-8'))


if __name__ == "__main__":
    connection()
