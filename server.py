import socket
from datetime import datetime, timedelta


class ClientEntity:
    def __init__(self, nickname):
        self.nickname = nickname
        self.last_visit = datetime.now()


class Server(object):
    def __init__(self, hostname, port):
        self.clients = {}

        # Создание сервера сокет
        self.udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # start server
        self.udp_server.bind((hostname, port))

        print("[INFO] Server running on {}:{}".format(hostname, port))

        while True:

            # Получаем данные от клиента
            data, addr = self.udp_server.recvfrom(1024)  # buffer size is 1024 bytes


            # Если клиент не зарегистрирован, добавьте в клиентский словарь
            if addr not in self.clients:
                print(f"New client connected: {addr}")

                self.clients[addr] = ClientEntity(data.decode())
                continue


            # Напечатать полученное сообщение и адрес клиента
            print(f"Received message from {addr}: {data.decode()}")


            # Разослать полученное сообщение всем остальным  клиентам
            self.send_message(data, addr)

    def send_message(self, message, addr):
        emojis = {
            ":)": "😊",
            ":(": "☹️",
            ":D": "😄",
            "<3": "❤️",
            "<>": "💩"
        }

        if len(self.clients) <= 0:
            return

        clients_to_remove = set()
        time_for_expire = datetime.now() - timedelta(hours=1)
        for client_addr in self.clients:
            client = self.clients[client_addr]
            # если это отправитель, то ему сообщение не отправляем, а время последней активности добавляем
            if client_addr == addr:
                client.last_visit = datetime.now()
                continue

            # если клиент не активничал в течении часа, то его следует удалить из рассылки
            if time_for_expire > client.last_visit:
                clients_to_remove.add(client_addr)
                continue

            msg = client.nickname + ": " + message.decode()

            # заменяем сообщения на смайлики
            for emoji, emoji_unicode in emojis.items():
                msg = msg.replace(emoji, emoji_unicode)

            self.udp_server.sendto(msg.encode(), client_addr)

        for c in clients_to_remove:
            del self.clients[c]


if __name__ == "__main__":
    port = 5555
    hostname = "localhost"

    chat_server = Server(hostname, port)