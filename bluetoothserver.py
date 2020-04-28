#Bluetooth socket modified from rfcomm-server.py Albert Huang
#Available at: https://github.com/karulis/pybluez/blob/master/examples/simple/rfcomm-server.py

from bluetooth import *
from threading import Thread
import sys
import queue

q = queue.Queue()


def blueSocket(conn):
    try:
        while True:
            data = conn.recv(1024)
            if len(data) != 0:
             #   break
                print("received [%s]" % data)
                q.put(data)
    except IOError:
        pass
    print("Disconnected")

def readerThread():
    print("Printing thread started")
    while True:
        msg = q.get()
        print(msg)


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
            bluconn = Thread(target=blueSocket, args=(client_sock,))
            bluconn.start()
            threads.append(bluconn)
        while True:
            print("Max connections reached: " + str(maxcons))
    except KeyboardInterrupt:
        sys.exit()

    
    server_sock.close()
    print("all done")

main()