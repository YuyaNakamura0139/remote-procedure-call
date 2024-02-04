import os
import json
import socket


sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

with open("./config.json") as f:
    config = json.load(f)

SERVER_ADDRESS = config["server_address"]

try:
    os.unlink(SERVER_ADDRESS)
except FileNotFoundError:
    pass

sock.bind(SERVER_ADDRESS)

sock.listen(1)

while True:
    connection, client_address = sock.accept()
    try:
        while True:
            data = connection.recv(1024)
            # デコード後の文字列をjsonに変換
            json_data = json.loads(data.decode("utf-8"))
            print(json_data)
            if data:
                message = "Have a nice day!"
                connection.sendall(message.encode("utf-8"))

    except Exception as e:
        print(e)
