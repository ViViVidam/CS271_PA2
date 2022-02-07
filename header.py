import threading
import time

clientIPs = [("127.0.0.1",5051),("127.0.0.1",5052),("127.0.0.1",5053),("127.0.0.1",5054)]
TEST = 1
NORMAL = 2
BANK = 1
MARKER = 2
clientGraph = [[0,1,0,0],
               [1,0,0,1],
               [0,1,0,0],
               [1,1,1,0]]
CLIENTNUM = len(clientIPs)

globalSnapshots = []
finished = []
globalStates = []

def monitor():
    lock = threading.Lock()
    while 1:
        time.sleep(6)
        with lock:
            print("\n\n*************FROM GLOBAL MONITOR****************",flush=True)
            for i in range(len(globalSnapshots)):
                print("\n-----------SNAPSHOT {}----------".format(globalSnapshots[i]),flush=True)
                print("clients that have submitted the snapshot: {}\n".format(finished[i],flush=True))
                printGlobalState(i)
                print("----------------------------------\n",flush=True)
            print("****************************************************\n\n",flush=True)

class State:
    def __init__(self,deposit,identifier,channelCount):
        self.deposit = deposit
        self.identifier = tuple(identifier)
        self.channelMessages = []
        for i in range(channelCount):
            self.channelMessages.append([])
    def record(self,index,data):
        self.channelMessages[index].append(data)
    def clear(self):
        self.deposit = 0
        for messages in self.channelMessages:
            messages.clear()
        self.identifier = (0,0)

class GlobalState:
    def __init__(self):
        self.clientStates = []
        for i in range(len(clientIPs)):
            self.clientStates.append(State(0,(),0))
    def setState(self,id,state):
        self.clientStates[id].deposit = state.deposit
        self.clientStates[id].channelMessages = state.channelMessages

def printGlobalState(index):
    for i in range(len(clientIPs)):
        print("{} deposit {}".format(i,globalStates[index].clientStates[i].deposit),flush=True)
        for j in range(len(globalStates[index].clientStates[i].channelMessages)):
            print("channel messages {}".format(globalStates[index].clientStates[i].channelMessages[j]),flush=True)
def submit_states(stateIdentifier,id,state):
    try:
        index = globalSnapshots.index(stateIdentifier)
    except:
        print("{} not int the {}".format(stateIdentifier,globalSnapshots),flush=True)
    globalStates[index].setState(id,state)