class Data:
    def __init__(self, data, ip):
        self.data = data
        self.ip = ip


class Server:
    _ip_counter = 1

    def __init__(self):
        self.buffer = []
        self.ip = Server._ip_counter
        Server._ip_counter += 1

    def send_data(self, data):
        router.buffer.append(data)

    def get_data(self):
        received_data = self.buffer[:]
        self.buffer.clear()
        return received_data

    def get_ip(self):
        return self.ip


class Router:
    def __init__(self):
        self.buffer = []
        self.servers = []

    def link(self, server):
        self.servers.append(server)

    def unlink(self, server):
        self.servers.remove(server)

    def send_data(self):
        for data in self.buffer:
            for server in self.servers:
                if server.get_ip() == data.ip:
                    server.buffer.append(data)
        self.buffer.clear()


router = Router()

