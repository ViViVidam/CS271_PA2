from client import Client
from header import *

clients = []
threads = []

def runCilents(i,mode):
    client = Client(i,mode)
    clients.append(client)
    client.run()
    print("client exit")
# Press the green button in the gutter to run the script.

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
