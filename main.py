import threading
from client import Client
from header import *
import time
clients = []
threads = []

def runCilents(i,mode):
    client = Client(i,mode)
    clients.append(client)
    client.run()
    print("client exit")
# Press the green button in the gutter to run the script.
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
if __name__ == '__main__':
    threading.Thread(target=monitor).start()
    for i in range(0,4):
        threads.append(threading.Thread(target=runCilents,args=(i,TEST)))
    print("launching server and client...")

    for thread in threads:
        thread.start()
    for thread in threads:
        if threads.index(thread) != 0:
            thread.join()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
