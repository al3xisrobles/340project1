# Alexis Robles and Eli Gottlieb
# 340 Project 1

###############################################
##### Part 3: Multi-Connection Web Server #####
###############################################

import socket
import sys
import select
import os

# Parse port
arg_lst = sys.argv
port = int(arg_lst[1])

# Create a TCP socket on which to listen for new connections
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind that socket to the port provided on the command line
server_socket.bind(('', port))

# Listen on that socket, which we shall call the "accept socket"
print(f"Server started on port {port}. Listening...")
server_socket.listen()

# Initialize the list of open connections to empty
open_connections = []

while True:

    # Use the select function to check for new connections, data to read, and sockets to close
    read_list, _, _ = select.select([server_socket] + open_connections, [], [])

    for sock in read_list:

        # If the server socket is ready, then a new connection is ready to be accepted
        if sock == server_socket:
            new_connection, _ = server_socket.accept()
            open_connections.append(new_connection)
            print("\nServer socket accepted.")
        else:
            # If a client socket is ready, then read data from it
            # Read the HTTP request from the connection socket and parse it
            request = sock.recv(1024)

            # If socket is closed by client, close the socket
            if not request:
                open_connections.remove(sock)
                sock.close()
                print("Socket closed.")

            # If request doesn't start with "GET", ignore it
            if not request.startswith(b"GET"):
                continue

            request_lines = request.decode().split("\r\n")
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

                sock.sendall(response.encode())

            elif not os.path.isfile(path):
                # Construct a HTTP error response (404 Not Found)
                response = "HTTP/1.1 404 Not Found\r\n"
                response += "Content-Type: text/html\r\n"
                response += "\r\n"
                response += "<html><body>404 Not Found</body></html>"
                sock.sendall(response.encode())
            else:
                # File exists, but does not end with ".htm" or "html"
                # Construct a HTTP error response (403 Forbidden)
                response = "HTTP/1.1 403 Forbidden\r\n"
                response += "Content-Type: text/html\r\n"
                response += "\r\n"
                response += "<html><body>403 Forbidden</body></html>"
                sock.sendall(response.encode())

            open_connections.remove(sock)
            sock.close()
            print("Socket closed.")
