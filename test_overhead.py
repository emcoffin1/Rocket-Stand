import socket
esp_ip = "192.168.4.1"
port = 80

def connect_to_esp():
    try:
        print("Connecting")
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((esp_ip, port))

        print("Connected")

        while True:
            data = client.recv(1024).decode().strip()
            if data:
                print(f"received: {data}")

    except KeyboardInterrupt:
        print("\n Stopping Connection")
    except Exception as e:
        print(f"Error: {e}")

    finally:
        client.close()


if __name__ == "__main__":
    connect_to_esp()
