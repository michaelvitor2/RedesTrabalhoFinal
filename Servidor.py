import socket
import struct
import random

class Packet:
    def __init__(self, seq_num, data, is_ack=False, ack_num=None):
        self.seq_num = seq_num
        self.data = data
        self.is_ack = is_ack
        self.ack_num = ack_num

def serialize(packet):
    header = struct.pack('!I?', packet.seq_num, packet.is_ack)
    if packet.is_ack:
        return header + struct.pack('!I', packet.ack_num)
    else:
        return header + packet.data.encode()

def deserialize(data):
    header = struct.unpack('!I?', data[:5])
    seq_num, is_ack = header
    if is_ack:
        ack_num = struct.unpack('!I', data[5:])[0]
        return Packet(seq_num=seq_num, data=None, is_ack=True, ack_num=ack_num)
    else:
        return Packet(seq_num=seq_num, data=data[5:].decode(), is_ack=False)

class PacketManager:
    def __init__(self):
        self.expected_seq_num = 0
        self.buffer = {}
        self.delivered = []

    def receive_packet(self, packet):
        print(f"Received packet with sequence number {packet.seq_num}")
        if packet.seq_num == self.expected_seq_num:
            self.deliver_packet(packet)
            self.expected_seq_num += 1

            while self.expected_seq_num in self.buffer:
                next_packet = self.buffer.pop(self.expected_seq_num)
                self.deliver_packet(next_packet)
                self.expected_seq_num += 1
        else:
            self.buffer[packet.seq_num] = packet

    def deliver_packet(self, packet):
        self.delivered.append((packet.seq_num, packet.data))
        print(f"Delivered packet #{packet.seq_num}: {packet.data}")

class Server:
    def __init__(self, port, loss_probability):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", port))
        self.packet_manager = PacketManager()
        self.loss_probability = loss_probability

    def send_ack(self, ack_num, addr):
        ack_packet = Packet(seq_num=0, data=None, is_ack=True, ack_num=ack_num)
        self.sock.sendto(serialize(ack_packet), addr)

    def run(self):
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                if random.random() < self.loss_probability:
                    print(f"Packet loss simulated for packet from {addr}")
                    continue
                
                packet = deserialize(data)
                if not packet.is_ack:
                    self.packet_manager.receive_packet(packet)
                    self.send_ack(packet.seq_num, addr)
                else:
                    print(f"Received ACK for packet #{packet.ack_num}")
            except Exception as e:
                print(f"An error occurred: {e}")

if __name__ == "__main__":
    loss_probability = 0.0
    server = Server(12345, loss_probability)
    server.run()
