# Alexis Robles and Eli Gottlieb
# 340 Project 1

#######################################
##### Part 2: A Simple Web Server #####
#######################################

import socket
import sys
import os

# Parse port
arg_lst = sys.argv
port = int(arg_lst[1])

# Create a TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a specific address and port
server_socket.bind(("", port))

# Begin listening for new connections
server_socket.listen()

while True:
    # Accept a new connection
    connection_socket, address = server_socket.accept()

    # Read the HTTP request from the connection socket and parse it
    request = connection_socket.recv(1024).decode()
    request_lines = request.split("\r\n")
    request_line = request_lines[0]
    request_parts = request_line.split(" ")
    method = request_parts[0]
    path = '.' + request_parts[1]

    # Check to see if the requested file exists (and ends with ".htm" or ".html")
    if os.path.isfile(path) and path.endswith(('.htm', '.html')):
        # Construct the appropriate HTTP response
        response = "HTTP/1.1 200 OK\r\n"
        response += "Content-Type: text/html\r\n"
        response += "\r\n"

        # Open the file and write its contents to the connection socket
        with open(path, "r") as file:
            response += file.read()

        connection_socket.sendall(response.encode())

    elif not os.path.isfile(path):
        # Construct a HTTP error response (404 Not Found)
        response = "HTTP/1.1 404 Not Found\r\n"
        response += "Content-Type: text/html\r\n"
        response += "\r\n"
        response += "<html><body>404 Not Found</body></html>"
        connection_socket.sendall(response.encode())
    else:
        # File exists, but does not end with ".htm" or "html"
        # Construct a HTTP error response (403 Forbidden)
        response = "HTTP/1.1 403 Forbidden\r\n"
        response += "Content-Type: text/html\r\n"
        response += "\r\n"
        response += "<html><body>403 Forbidden</body></html>"
        connection_socket.sendall(response.encode())

    # Close the connection socket
    connection_socket.close()
