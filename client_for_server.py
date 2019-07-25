import zmq
from threading import Thread
import queue
from client_login import LoginClient


class Client:
    def __init__(self, username, server_address, server_router_ID, target):
        self.context = zmq.Context.instance()
        self.username = username
        self.server_address = server_address
        self.q = queue.Queue()
        self.message = None
        self.server_router_ID = server_router_ID
        self.target = target

    def run(self):
        if self.login():
            self.relay()

        # heartbeat = Thread(target=self.heartbeat)
        # heartbeat.daemon = True
        # heartbeat.start()

    def relay(self):
        main_socket = self.context.socket(zmq.DEALER)
        main_socket.setsockopt(zmq.IDENTITY, self.username.encode())
        main_socket.connect("tcp://localhost:{}".format(self.server_address))

        inputting = Thread(target=self.input_message)
        inputting.daemon = True
        inputting.start()
        print('Client connected!\n')
        while True:
            if main_socket.poll(1):
                incoming_message = main_socket.recv_json()
                self.message_received(incoming_message)
            if not self.q.empty():
                client_message = self.q.get()
                data = {'to': self.target,
                        'message': client_message}

                main_socket.send_json(data)

    def input_message(self):
        while True:
            self.message = input('')
            self.q.put(self.message)

    @staticmethod
    def message_received(incoming_message):
        ID = incoming_message['id']
        new_message = incoming_message['message']
        print('{}: {}'.format(ID, new_message))
        return

    # def heartbeat(self):
    # heart_socket = self.context.socket(zmq.DEALER)
    # heart_socket.setsockopt(zmq.IDENTITY, self.username)
    # heart_socket.connect("tcp://localhost:{}".format('5556'))
    def login(self):
        login = LoginClient('5557')
        return login.login()
