import socket
import time
import queue
import threading

# Constants
HOST = '127.0.0.1' 
PORT = 12000
NUMBER_OF_THREADS = 3

# Global Variables
serverSocket = None
clientConnections = []
clientAddresses = []
queue = Queue()

# Working area
# ------------------------------Thread 1 -----------------------------
# Create a socket
def create_socket():
    global serverSocket

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket
def bind_socket():
    global serverSocket

    # Bind takes a tuple!
    serverSocket.bind((HOST, PORT))

    # Listen to te socket
    serverSocket.listen(5)

# Accept connetion
def accept_connection():
    global serverSocket
    global clientConnections
    global clientAddresses

    # Flush all previous connections
    for connection in clientConnections:
        connection.close()

    del clientConnections[:]
    del clientAddresses[:]

    try:
        clientConnection, clientAddress = serverSocket.accept()

        clientConnections.append(clientConnection)
        clientAddresses.append(clientAddress)

        print(clientAddress[0] + " just connected")
    except:
        print("Error in accepting connections")

# Serve the connection
# ------------------------------Thread 2 -----------------------------
# Fire up the terminal
def start_terminal():
    while True:

        # Get command
        command = input("Nightingale>")
        
        # 1. List all the connected clients
        if command == "list":
            list_connected()
        
        # 2. Select a client and send commands to that client
        elif "select" in command:
            clientConnection = get_client(command)
            if clientConnection is not None:
                send_client_commands(clientConnection)

        # 3. Exit
        elif command == "exit":
            break

        else:
            print("Error no such command...")

# Display all the connected clients
def list_connected():
    global clientConnections
    global clientAddresses

    client = ""

    # Loop through all the clients and check the active ones
    for i, connection in enumerate(clientConnections):
        try:
            # Ping client
            connection.send(str.encode('@'))
        except:
            # Delete the client from the list
            del clientConnections[i]
            del clientAddresses[i]
            continue
        # Store the active client address
        client += str(i) + " " + str(clientAddresses[i][0] + " " + str(clientAddresses[i][1]))

    # Display active clients
    print("------------------Clients-------------\n" + client)

# Retuns the required client's connection
def get_client(command):
    global clientConnections
    global clientAddresses

    try:
        # Get client number from the command
        # command => select 1
        client = int(command[7:])

        # Get the client connection
        clientConnection = clientConnections[client]

        # Inform connection
        print("You are now connected to: " + str(clientAddresses[client][0]))
        
        # Return the client connection
        return clientConnection
    except:
        print("Invalid selection")

def send_client_commands(clientConnection):
    while True:
        # Get Command
        command = input()

        # Check command for exit
        if command == "exit":
            break

        # Encode command 
        command = command.encode()

        # Send command to the client
        if len(command) > 0:
            try:
                clientConnection.sendall(command)

                # Recieve response
                clientResponse = clientConnection.recv(2048)

                # Decode response
                clientResponse = clientResponse.decode()

                # Display response
                print(clientResponse, end='')
            except:
                print("Error sending commands")
                break
# ------------------------------Thread 3 -----------------------------
def ping_clients():
    global clientConnections
    global clientAddresses

    while True:
        try:
            # Loop through all the clients and check the active ones
            for i, connection in enumerate(clientConnections):
                try:
                    # Ping client
                    connection.send(str.encode('@'))
                except:
                    # Delete the client from the list
                    del clientConnections[i]
                    del clientAddresses[i]
                    continue
        except:
            break
        time.sleep(5)

# create jobs
def create_jobs():
    global queue

    for i in range(1, NUMBER_OF_THREADS + 1):
        queue.put(i)

    queue.join() # Halt the main thread

def create_threads():

    for i in range(NUMBER_OF_THREADS):
        thread = threading.Thread(target=work)
        thread.daemon = True # make it a background process
        thread.start()

def work():
    global queue

    while True:
        job = queue.get()
        if job == 1:
            create_socket()
            bind_socket()
            accept_connection()
        elif job == 2:
            start_terminal()
        elif job == 3:
            ping_clients()

create_threads()
create_jobs()