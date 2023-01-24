# Alexis Robles and Eli Gottlieb
# 340 Project 1

######################################
##### Part 4: Dynamic Web Server #####
######################################

import socket
import sys
import json

# Parse port
arg_lst = sys.argv
port = int(arg_lst[1])

# Create a TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind port to socket
server_socket.bind(('', port))

# Listen for incoming connections
server_socket.listen()

def send_bad_request():
    response = "HTTP/1.1 400 Bad Request\r\n"
    response += "Content-Type: text/html\r\n"
    response += "\r\n"
    response += "<html><body>400 Bad Request</body></html>"
    client_socket.sendall(response.encode())
    client_socket.close()

while True:
    # Accept a new connection
    client_socket, client_address = server_socket.accept()

    # Read data from the client socket
    data = client_socket.recv(1024)

    # Decode the data to a string
    data = data.decode()

    # Split the data into lines
    lines = data.split("\n")

    # Get the first line, which should contain the GET request
    request_line = lines[0]

    # Split the request line into parts
    parts = request_line.split(" ")

    # Get the request method (should be GET) and the request path
    method, path = parts

    # Check if the request method is GET and the request path is "/product"
    if method == "GET" and path.startswith("/product"):

        # Get the query parameters from the request path
        if len(path.split("?")) > 1:
            query_string = path.split("?")[1]
        else:
            send_bad_request()
            continue

        try:
            query_parameters = query_string.split("&")
            a = float(query_parameters[0].split("=")[1])
            b = float(query_parameters[1].split("=")[1])
            c = float(query_parameters[2].split("=")[1])

            # Perform the multiplication
            result = a * b * c

            # Create the JSON response
            response = {
                "operation": "product",
                "operands": [a, b, c],
                "result": result
            }
            # Encode the JSON response to a string
            response_json = json.dumps(response)

            # Send the headers to the client
            headers = "HTTP/1.1 200 OK\n"
            headers += "Content-Type: application/json\n"
            headers += "Content-Length: {}\n".format(len(response_json))
            headers += "\n"
            client_socket.sendall(headers.encode())

            # Send the response to the client
            client_socket.sendall(response_json.encode())
        except ValueError:
            send_bad_request()
            continue
    else:
        # Send a error response
        response = "HTTP/1.1 400 Bad Request\n\n"
        client_socket.sendall(response.encode())

    # Close the client socket
    client_socket.close()
