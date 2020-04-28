#Bluetooth socket modified from rfcomm-server.py Albert Huang
#Available at: https://github.com/karulis/pybluez/blob/master/examples/simple/rfcomm-server.py

from bluetooth import *
from threading import Thread
import sys
import queue
import tkinter as tk

q = queue.Queue()


def blueSocket(conn, index):
    try:
        while True:
            data = conn.recv(1024)
            if len(data) != 0:
                #print("received [%s]" % data)
                datastr = str(index) + ";" + data.decode("utf-8")
                q.put(datastr)
    except IOError:
        print("Disconnected")
        pass
    

def readerThread():
    print("Printing thread started")
    master = tk.Tk()
    sockets = {}
    rows = 0
    while True:
        msg = q.get()
        print(msg)
        sockId, data = msg.split(";")
        if sockId not in sockets:
            sockRow = rows
            rows += 1
            sockets[sockId] = []
            tk.Label(master, text="Connection " + sockId + " newest acceleration: ").grid(row=sockRow)
            accLabel = tk.Label(master, text="")
            accLabel.grid(row=sockRow, column=1)
            sockets[sockId].append(accLabel)
            tk.Label(master, text="Current stepcount: ").grid(row=sockRow, column=2)
            stepLabel = tk.Label(master, text="0")
            stepLabel.grid(row=sockRow, column=3)
            sockets[sockId].append(stepLabel)
            tk.Label(master, text="Activity (%): ").grid(row=sockRow, column=4)
            actLabel = tk.Label(master, text="")
            actLabel.grid(row=sockRow, column=5)
            sockets[sockId].append(actLabel)
        accLabel = sockets[sockId][0]
        stepLabel = sockets[sockId][1]
        actLabel = sockets[sockId][2]
        data = data.split(",")
        accLabel['text'] = data[0]
        lastSteps = int(stepLabel["text"])
        lastSteps += int(data[1])
        stepLabel['text'] = str(lastSteps)
        master.update()



def main():
    maxcons = 4
    threads = []
    worker = Thread(target=readerThread)
    worker.start()

    try:
        for i in range(maxcons):
            server_sock=BluetoothSocket( RFCOMM )
            server_sock.bind(("",PORT_ANY))
            server_sock.listen(1)

            port = server_sock.getsockname()[1]
            uuid = "d2e1c93a-887d-11ea-bc55-0242ac130003"

            advertise_service( server_sock, "GymActivityServer",
                            service_id = uuid,
                            service_classes = [ uuid, SERIAL_PORT_CLASS ],
                            profiles = [ SERIAL_PORT_PROFILE ], 
            #                   protocols = [ OBEX_UUID ] 
                                )

            print("Waiting for connection on RFCOMM channel %d" % port)

            client_sock, client_info = server_sock.accept()
            print("Accepted connection from ", client_info)
            stop_advertising(server_sock)
            bluconn = Thread(target=blueSocket, args=(client_sock,i))
            bluconn.start()
            threads.append(bluconn)
        while True:
            print("Max connections reached: " + str(maxcons))
    except KeyboardInterrupt:
        sys.exit()

    
    server_sock.close()
    print("all done")

main()