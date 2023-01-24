# Alexis Robles and Eli Gottlieb
# 340 Project 1

#######################################
##### Part 1: A Simple Curl Clone #####
#######################################

import sys
import socket

# /*
#   INPUT PARSING
#                */

# Parse web address
arg_lst = sys.argv
web_addr = arg_lst[1]

# Trying to use TLS for HTTPS
if web_addr.startswith("https") :
    print("Do not use a web address using TLS. Use a non-secure address.", file=sys.stderr)
    sys.exit(1)

# Web address does not start with http://
if not web_addr.startswith("http://"):
    sys.exit(1)

# Remove prefixes in web address
web_addr = web_addr.split('//')[1]

# Remove / at end of web address
web_addr = web_addr[:-1] if web_addr[-1] == '/' else web_addr

# Parse port
try:
    web_port = web_addr.split(':')[1]
    web_port = int(web_port.split('/')[0])
except IndexError:
    web_port = 80

# Parse web address path
try:
    web_addr_path = web_addr.split('/')[1]
    web_addr = web_addr.split('/')[0]
    try:
        web_addr = web_addr.split(':')[0]
    except:
        pass
except IndexError:
    web_addr_path = ''

# Make sure port is removed from web address
if ":" in web_addr:
    web_addr = web_addr[:web_addr.index(":")]

# /*
#   GET REQUEST
#              */

def format_location_port_and_port(location):
    port = 80

    # Trying to use TLS for HTTPS
    if location.startswith(b"https") :
        print("Do not use a web address using TLS. Use a non-secure address.", file=sys.stderr)
        sys.exit(1)

    # Web address does not start with http://
    if not location.startswith(b"http://"):
        sys.exit(1)

    location = location.decode().split("//")[1]
    location = location[:-1] if location[-1] == '/' else location
    try:
        path = location.split('/')[1]
        location = location.split('/')[0]
    except IndexError:
        path = ''
    if 'www.' in location:
        location = location.split('www.')[1]
    try:
        port = int(location.split(':')[1])
    except IndexError:
        pass
    location = location.split(':')[0]

    return (location, port, path)

def get_request(url, port, path, redirect_count=0, redirect_limit=10):


    # Create a socket object for the client
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Translate host name to IPv4 address format
    host = socket.gethostbyname(url)

    # Connect to hostname on the specified port, or 80 by default.
    client_socket.connect((host, port))

    # Send a GET request
    get_msg = f'GET /{path} HTTP/1.1\r\nHost: {url}\r\n\r\n'
    client_socket.sendall(bytes(get_msg, 'utf-8'))

    # Receive data from the server (up to 1024 bytes)
    data = client_socket.recv(1024)

    # Print content type if it's text/html
    content_type = data.decode().split('Content-Type')[1][2:11]
    if not content_type == "text/html":
        print("Content type is not text/html.", file=sys.stderr)
        sys.exit(1)

    # Handle redirects then close the socket
    status_code = data.split(b' ')[1]
    if redirect_count < redirect_limit and (status_code == b'301' or status_code == b'302'):
        location = None
        headers = data.split(b'\r\n')
        for header in headers:
            if header.startswith(b'Location: '):
                location = header.split(b' ')[1]
                break
        if location:
            client_socket.close()

            # Fix location and port syntax
            (location, port, path) = format_location_port_and_port(location)

            print(f"Redirecting to {location}/{path} on port {port}\n", file=sys.stderr)
            return get_request(location, port, path, redirect_count+1, redirect_limit)
    else:
        client_socket.close()
        if redirect_count == redirect_limit:
            print('Redirect limit exceeded.', file=sys.stderr)
            sys.exit(1)
        return data.decode()

response = get_request(web_addr, web_port, web_addr_path, 0, 10)

# Ensure status code is below 400, or else exit with exit code 1
status_code = int(response.split('1.1')[1][1:4])
response_body = response.split('\r\n\r\n')[1]
if status_code == 200:
    print(response_body, file=sys.stdout)
    sys.exit(0)
if status_code >= 400:
    print(response_body, file=sys.stdout)
    sys.exit(1)
