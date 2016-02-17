#!/usr/bin/env python
# -*- coding=utf-8 -*-

import socket
import sys
import select
from protocol import JsonProtocel

__author__ = 'Riky'

ACT_CON = 1
ACT_CHAT = 2
ACT_EXIT = 3
ACT_SYSTEM = 4


class Client(object):
    def __init__(self, host, port=0):
        self.host = host
        self.port = port
        self.nickname = ''
        self.client = self.connect()

    def connect(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
            print 'Input your nickname please!'
            print 'Nickname:'
            self.nickname = raw_input()
            pack_msg = JsonProtocel.pack(nickname=self.nickname, content='', action=ACT_CON)
            sock.send(pack_msg)

        except socket.error:
            print 'Could not connect to server %s:%d' % (self.host, self.port)
            sys.exit(1)

        print 'Connected to server %s:%d' % (self.host, self.port)
        return sock

    def run(self):
        running = True
        while running:
            try:
                #sys.stdout.write(self.prompt)
                #sys.stdout.flush()

                # Wait for input from stdin & socket
                inputready, outputready, exceptrdy = select.select([0, self.client], [], [])

                for i in inputready:
                    if i == 0:
                        # grab message
                        data = sys.stdin.readline().strip()
                        if data:
                            pack_data = JsonProtocel.pack(data, ACT_CHAT, self.nickname)
                            self.client.send(pack_data)

                    elif i == self.client:
                        data = self.client.recv(1024)

                        if not data:
                            print 'Shutting down.'
                            running = False
                            break

                        else:
                            data = JsonProtocel.unpack(data)
                            if data['action'] is ACT_CHAT:
                                msg = '['+data['nickname']+']:'+data['content']
                            elif data['action'] is ACT_CON:
                                msg = '[system]:'+data['content']
                            elif data['action'] is ACT_SYSTEM:
                                msg = '['+data['nickname']+']:'+data['content']
                            elif data['action'] is ACT_SYSTEM:
                                msg = '['+data['nickname']+']:'+data['content']
                            else:
                                break
                            sys.stdout.write(msg+'\n')
                            sys.stdout.flush()

            except KeyboardInterrupt:
                msg = "leavel the chat room."
                pack_data = JsonProtocel.pack(msg, ACT_EXIT, self.nickname)
                self.client.send(pack_data)
                self.client.close()
                break


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit('Usage: python %s listen_ip listen_port' % sys.argv[0])

    host = sys.argv[1]
    port = int(sys.argv[2])
    client = Client(host, port)
    client.run()
