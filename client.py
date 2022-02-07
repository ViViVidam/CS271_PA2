import socket
import threading
import time
import json
import sys
from header import *


class UDPSocket:
    buffersize = 1024

    def __init__(self, id):
        self.address = clientIPs[id]
        self.UDPsocket = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPsocket.bind(self.address)

    def sendMessage(self, message, ip):
        time.sleep(3)
        msgByte = str.encode(json.dumps(message))
        self.UDPsocket.sendto(msgByte, ip)

    def recvMessage(self):
        data, clientIP = self.UDPsocket.recvfrom(self.buffersize)
        data = json.loads(data.decode())
        return data, clientIP


class Client:
    def __init__(self, id, mode):
        self.mode = mode  # 1:normal 2:test
        self.socket = UDPSocket(id)
        self.id = id
        self.lock = threading.Lock()
        self.clock = 0

        self.deposit = 10
        self.finish = False  # for test
        self.states = []
        self.markersRecv = []
        self.outChannel = []
        self.inChannel = []
        for i in range(len(clientGraph[self.id])):
            if clientGraph[self.id][i] == 1:
                self.outChannel.append(i)
            if clientGraph[i][self.id] == 1:
                self.inChannel.append(i)

        self.channelSize = len(self.inChannel)

    def getStateIndex(self, identifier):
        identifier = tuple(identifier)
        with self.lock:
            for state in self.states:
                if identifier == state.identifier:
                    return self.states.index(state)
            return -1

    def initSnapshot(self, sender, sequence):
        tempStateId = 0  # two init snapshot is possible, so it might overwrite the actual id we need to validate
        with self.lock:
            print("{} initial a snapshot with tag {}".format(self.id, sequence))
            temp = State(self.deposit, sequence, self.channelSize)
            if tuple(sequence) not in globalSnapshots:
                globalSnapshots.append(tuple(sequence))
                finished.append([])
                globalStates.append(GlobalState())
            self.states.append(temp)
            tmpBuf = []
            for i in range(CLIENTNUM):
                if(clientGraph[i][self.id] == 0):
                    tmpBuf.append(1)
                else:
                    tmpBuf.append(0)
            tmpBuf[sender] = 1
            self.markersRecv.append(tmpBuf)
            tempStateId = len(self.markersRecv) - 1
        self.checkRecv(tempStateId)
        payload = {'id': self.id, 'op': MARKER, 'data': sequence}
        self.broadcastMARKER(sender, payload)

    def broadcastMARKER(self, sender, data):
        stateIndex = self.getStateIndex(data['data'])
        for client in self.outChannel:
            print("{} broadcast states{}'s (tag {}) MARKER to {}".format(
                self.id, stateIndex, data['data'], client))
            self.socket.sendMessage(data, clientIPs[client])

    def endSnapshot(self, stateIndex):
        with self.lock:
            finished[globalSnapshots.index(
                self.states[stateIndex].identifier)].append(self.id)
            print("{} Ending Snapshot. State identifier {}".format(
                self.id, self.states[stateIndex].identifier), flush=True)
            submit_states(self.states[stateIndex].identifier,
                          self.id, self.states[stateIndex])
            '''
            print("{} deposit {}".format(self.id,self.states[stateIndex].deposit), flush=True)
            for index in range(self.channelSize):
                print("{} incoming channel {} {}:".format(self.id,self.inChannel[index],self.states[stateIndex].channelMessages[index]), flush=True)
            '''
            self.states.pop(stateIndex)
            self.markersRecv.pop(stateIndex)

    def record(self, clientId, transaction):
        print("{} safe {} corresponding channel message {}".format(
            self.id, clientId, transaction))
        with self.lock:
            for i in range(len(self.states)):
                if self.markersRecv[i][clientId] == 0:
                    self.states[i].record(
                        self.inChannel.index(clientId), transaction)

    def checkRecv(self, stateIndex):
        print("{} recv state {} {}".format(
            self.id, self.states[stateIndex].identifier, self.markersRecv[stateIndex]))
        flag = 0
        for item in self.markersRecv[stateIndex]:
            if item != 1:
                flag = 1
                break
        if flag == 0:
            self.endSnapshot(stateIndex)

    def listen(self):
        while(1):
            data, sender = self.socket.recvMessage()
            if data['op'] == BANK:
                with self.lock:
                    self.deposit += data['data']
                print("{} transfer received {}".format(self.id, data['data']))
                if len(self.states) != 0:
                    self.record(data['id'], (data['id'], data['data']))
            elif data['op'] == MARKER:
                print("{} received MARKER from {} with tag {}".format(
                    self.id, data['id'], data['data']))
                stateIndex = self.getStateIndex(data['data'])
                if stateIndex == -1:
                    self.initSnapshot(data['id'], data['data'])
                    with self.lock:
                        self.clock += 1
                else:
                    self.markersRecv[stateIndex][data['id']] = 1
                    self.checkRecv(stateIndex)

    def read(self):
        val = 0
        while(1):
            while (val != 't' and val != 'c' and val != 's' and val !='d'):
                val = input("May I help you? (t for transfer, c for check balance , s for snapshot, to view the snapshots: d): ")
            if val == 'c':
                val = 0
                print("your deposit: {}".format(self.deposit))
            elif val == 't':
                val = 0
                while(1):
                    val = input("to who? (0-3): ")
                    val = int(val)
                    if val <= 3 and val >= 0 and clientGraph[self.id][val] == 1:
                        break
                money = input('how much ?')
                money = int(money)
                if(self.deposit < money):
                    print("INSUFFICIENT BALANCE")
                else:
                    print("your deposit: {}".format(self.deposit))
                    payload = {'id': self.id, 'op': BANK, 'data': money}
                    self.socket.sendMessage(payload, clientIPs[val])
                    with self.lock:
                        self.deposit -= money
                    print('SUCCESS')
                    print("your deposit: {}".format(self.deposit))
            elif val == 's':
                val = 0
                ### tag: (id, clock)
                self.initSnapshot(self.id, (self.id, self.clock))
                with self.lock:
                    self.clock += 1
            elif val == 'd':
                val = 0
                with self.lock:
                    print("\n\n*************FROM GLOBAL MONITOR****************", flush=True)
                    for i in range(len(globalSnapshots)):
                        print("\n-----------SNAPSHOT {}----------".format(globalSnapshots[i]), flush=True)
                        print("clients that have submitted the snapshot: {}\n".format(finished[i], flush=True))
                        printGlobalState(i)
                        print("----------------------------------\n", flush=True)
                    print("****************************************************\n\n", flush=True)
            else:
                print("invalid input {}".format(val))

    def test(self):
        file = open("test{}".format(self.id))
        for line in file.readlines():
            operations = line[:-1].split(' ')  # remove '\n'
            operations = list(map(int, operations))
            if operations[0] == 0:
                print("your deposit: {}".format(self.deposit))
            elif operations[0] == 1 or operations[0] == 2:
                self.initSnapshot(self.id, (self.id, self.clock))
                with self.lock:
                    self.clock += 1
            else:
                money = operations[3]
                if(self.deposit < money):
                    print("INSUFFICIENT BALANCE")
                else:
                    print("{} transfer {} to {}".format(
                        self.id, money, operations[2]))
                    payload = {'id': self.id, 'op': BANK, 'data': money}
                    self.socket.sendMessage(payload, clientIPs[operations[2]])
                    with self.lock:
                        self.deposit -= money
            time.sleep(2)

    def run(self):
        listenThread = threading.Thread(target=self.listen)
        if self.mode == TEST:
            sendThread = threading.Thread(target=self.test)
        else:
            sendThread = threading.Thread(target=self.read)
        listenThread.start()
        time.sleep(1)
        sendThread.start()
        listenThread.join()
        sendThread.join()


if __name__ == '__main__':
    client = Client(int(sys.argv[1]), NORMAL)
    print("{} client started\nlistening...".format(client.id))
    client.run()
