#Bluetooth socket modified from rfcomm-server.py Albert Huang
#Available at: https://github.com/karulis/pybluez/blob/master/examples/simple/rfcomm-server.py

from bluetooth import *
from threading import Thread
from socket import timeout
import sys
import queue
import tkinter as tk
import time

q = queue.Queue()


def blueSocket(conn, index):
    conn.settimeout(30)
    try:
        while True:
            data = conn.recv(1024)
            if len(data) != 0:
                #print("received [%s]" % data)
                datastr = str(index) + ";" + data.decode("utf-8")
                q.put(datastr)
            else:
                print("Disconnected")
                q.put(str(index) + ";" + "0")
                return
    except (IOError, timeout):
        print("Disconnected")
        q.put(str(index) + ";" + "0")
        return
    

def readerThread():
    print("Printing thread started")
    master = tk.Tk()
    master.geometry("1600x900")
    sockets = {}
    rows = 0
    while True:
        msg = q.get()
        #print(msg)
        sockId, data = msg.split(";")
        if sockId not in sockets:
            sockRow = int(sockId) + 1
            rows += 1
            sockets[sockId] = []
            tk.Label(master, text="Connection " + sockId + " newest acceleration: ", font=(('Arial', 24))).grid(row=sockRow)
            accLabel = tk.Label(master, text="", width=6, font=(('Arial', 24)))
            accLabel.grid(row=sockRow, column=1)
            sockets[sockId].append(accLabel)
            tk.Label(master, text="Current stepcount: ", font=(('Arial', 24))).grid(row=sockRow, column=2)
            stepLabel = tk.Label(master, text="0", font=(('Arial', 24)), width=4)
            stepLabel.grid(row=sockRow, column=3)
            sockets[sockId].append(stepLabel)
            tk.Label(master, text="Activity (%): ", font=(('Arial', 24))).grid(row=sockRow, column=4)
            actLabel = tk.Label(master, text="", font=(('Arial', 24)), width=3)
            actLabel.grid(row=sockRow, column=5)
            sockets[sockId].append(actLabel)
            tk.Label(master, text="Active now: ", font=(('Arial', 24))).grid(row=sockRow, column=6)
            statLabel = tk.Label(master, text="", font=(('Arial', 24)), width=3)
            statLabel.grid(row=sockRow, column=7)
            sockets[sockId].append(statLabel)
            sockets[sockId].append([0,0])   #Counter for active (0) and inactive (1) states
            sockets[sockId].append([0, 0, 0, 0, 0])
        #print(sockets[sockId])
        if data == "0":
            #rip socket
            for widg in master.grid_slaves():
                if int(widg.grid_info()["row"]) == (int(sockId) + 1):
                    widg.grid_forget()
            master.update()
            continue
        accLabel = sockets[sockId][0]
        stepLabel = sockets[sockId][1]
        actLabel = sockets[sockId][2]
        statLabel = sockets[sockId][3]
        data = data.split(",")
        accLabel['text'] = data[0]
        lastSteps = int(stepLabel["text"])
        lastSteps += int(data[1])
        stepLabel['text'] = str(lastSteps)
        sockets[sockId][5].pop(0)
        sockets[sockId][5].append(float(data[0]))
        average = sum(sockets[sockId][5]) / 5
        if average > 3.0 or int(data[1]) > 0:
            sockets[sockId][4][0] += 1
            statLabel['text'] = "Yes"
            statLabel.config(bg="green")
        else:
            sockets[sockId][4][1] += 1
            statLabel['text'] = "No"
            statLabel.config(bg="red")
        activePerc = sockets[sockId][4][0] / (sockets[sockId][4][0] + sockets[sockId][4][1])
        activePerc = int(round(activePerc * 100))
        actLabel['text'] = str(activePerc)
        master.update()



def main():
    maxcons = 4
    threads = []
    worker = Thread(target=readerThread)
    worker.start()
    i = 0
    try:
        while True:
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
            i += 1
            bluconn.start()
            threads.append(bluconn)
            if len(threads) > maxcons:
                while len(threads) > maxcons:
                    print("Max connections reached: " + str(maxcons))
                    time.sleep(2)
                    alivethreads = []
                    for t in threads:
                        if t.isAlive():
                            alivethreads.append(t)
                    threads = alivethreads
    except KeyboardInterrupt:
        sys.exit()

    
    server_sock.close()
    print("all done")

main()