#!/usr/bin/env python
# -*- coding=utf-8 -*-

import socket
import signal
import select
import sys
import time
from protocol import JsonProtocel

__author__ = 'Riky'

ACT_CON = 1
ACT_CHAT = 2
ACT_EXIT = 3
ACT_SYSTEM = 4


class JanServer(object):
    def __init__(self, host='localhost', port=3333):
        self.host = host
        self.port = port
        self.client = 0
        self.client_map = {}
        self.output_clients = []
        self.input_clients = []

        self.connect()

        # Trap keyboard interrupts
        signal.signal(signal.SIGINT, self.call_back)
        pass

    def connect(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        print 'Listening to port', port

    def call_back(self, signum, frame):
        print "Shutting down service."
        for client in self.output_clients:
            client.close()
        self.server.close()
        sys.exit(0)

    def run(self):
        self.input_clients = [self.server, sys.stdin]

        runing_flag = True

        while runing_flag:
            try:
                input_ready, output_ready, except_ready = select.select(self.input_clients, self.output_clients, [])
            except select.error:
                break
            except socket.error:
                break

            for s in input_ready:
                if s == self.server:
                    new_client, new_address = self.server.accept()
                    self.client += 1
                    self.input_clients.append(new_client)
                    self.client_map[new_client] = {'address': new_address}
                    msg = " Welcome to the chat room."
                    self.send(JsonProtocel.pack(msg, ACT_SYSTEM, "system"), [new_client])
                    self.output_clients.append(new_client)
                elif s == sys.stdin:
                    # stop running
                    sys.stdin.readlines()
                    runing_flag = False
                else:
                    try:
                        data = self.recieve(s)
                        print data
                        if data:
                            if data['action'] == ACT_CON:
                                msg = str.title(data['nickname']) + " joined the chat room."
                                self.send(JsonProtocel.pack(msg, ACT_SYSTEM, "system"), self.output_clients)
                            elif data['action'] == ACT_CHAT:
                                msg = data['content']
                                self.send(JsonProtocel.pack(msg, ACT_SYSTEM, data['nickname']), self.output_clients)
                            elif data['action'] == ACT_EXIT:
                                msg = data['nickname'] + ' ' + data['content']
                                self.send(JsonProtocel.pack(msg, ACT_SYSTEM, 'system'), self.output_clients)
                        else:
                            self.client -= 1
                            s.close()
                            self.output_clients.remove(s)
                            self.input_clients.remove(s)
                            # send outline to other
                    except socket.error:
                        self.output_clients.remove(s)
                        self.input_clients.remove(s)
            time.sleep(0.1)
        self.server.close()

    def send(self, msg, to_clients):
        """
        send data
        """
        try:
            for s in to_clients:
                s.send(msg)
                print msg
                print s
        except socket.error:
            to_clients.remove(s)
            self.input_clients.remove(s)

    def recieve(self, server):
        """
        recieve data
        """
        buff = server.recv(1024)
        return JsonProtocel.unpack(buff)


if __name__ == '__main__':

    if len(sys.argv) < 3:
        sys.exit('Usage: python %s listen_ip listen_port' % sys.argv[0])

    host = sys.argv[1]
    port = int(sys.argv[2])
    print host
    print port
    server = JanServer(host, port)
    server.run()
