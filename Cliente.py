import socket
import struct
import random
import time
import csv

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

class Client:
    def __init__(self, server_ip, server_port, loss_probability):
        self.server_ip = server_ip
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(1)
        self.seq_num = 0
        self.cwnd = 1
        self.ssthresh = 64
        self.ack_num_received = 0
        self.loss_probability = loss_probability
        self.sent_times = {}  # Armazena tempos de envio dos pacotes

    def send_packet(self, data):
        packet = Packet(seq_num=self.seq_num, data=data)
        self.sock.sendto(serialize(packet), (self.server_ip, self.server_port))
        self.sent_times[self.seq_num] = time.time()  # Registro do tempo de envio
        self.seq_num += 1

    def receive_ack(self):
        data, _ = self.sock.recvfrom(1024)
        ack_packet = deserialize(data)
        if ack_packet.is_ack:
            return ack_packet.ack_num

    def congestion_control(self, ack_num):
        if ack_num > self.ack_num_received:
            self.ack_num_received = ack_num
            if self.cwnd < self.ssthresh:
                self.cwnd += 1
            else:
                self.cwnd += 1 / self.cwnd
        else:
            self.ssthresh = max(int(self.cwnd / 2), 1)
            self.cwnd = 1

    def run(self, data_list, log_file, latency_file):
        base = 0
        start_time = time.time()
        checkpoints = [100, 200, 500, 1000]
        next_checkpoint = checkpoints.pop(0)
        with open(log_file, 'w', newline='') as csvfile, open(latency_file, 'w', newline='') as lat_file:
            fieldnames = ['num_packets', 'time_elapsed', 'throughput']
            lat_fieldnames = ['seq_num', 'latency']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            lat_writer = csv.DictWriter(lat_file, fieldnames=lat_fieldnames)
            writer.writeheader()
            lat_writer.writeheader()
            
            while base < len(data_list):
                next_seq_num = int(min(base + self.cwnd, len(data_list)))
                for i in range(base, next_seq_num):
                    if random.random() < self.loss_probability:  # Simulação de perda
                        print(f"Packet {self.seq_num} lost")
                        self.seq_num += 1
                        continue
                    self.send_packet(data_list[i])
                    print(f"Sent: {data_list[i]}")
                
                try:
                    ack_num = self.receive_ack()
                    print(f"ACK received for packet {ack_num}")
                    self.congestion_control(ack_num)
                    base = ack_num + 1
                    # Calcular latência
                    latency = time.time() - self.sent_times.pop(ack_num, start_time)
                    lat_writer.writerow({'seq_num': ack_num, 'latency': latency})
                except socket.timeout:
                    print("Timeout waiting for ACK")
                    self.ssthresh = max(int(self.cwnd / 2), 1)
                    self.cwnd = 1
                
                num_packets = base
                if num_packets >= next_checkpoint:
                    time_elapsed = time.time() - start_time
                    if time_elapsed > 0:  # Evitar divisão por zero
                        throughput = num_packets / time_elapsed
                        writer.writerow({'num_packets': num_packets, 'time_elapsed': time_elapsed, 'throughput': throughput})
                        print(f"{num_packets} packets sent in {time_elapsed:.2f} seconds with throughput {throughput:.2f} packets/second")
                    if checkpoints:
                        next_checkpoint = checkpoints.pop(0)
                    else:
                        break

if __name__ == "__main__":
    data_list = [f"Message {i}" for i in range(1, 1001)]
    
    print("Running without packet loss...")
    client = Client("127.0.0.1", 12345, loss_probability=0.0)
    client.run(data_list, 'without_loss.csv', 'latency_without_loss.csv')
    
    print("Running with packet loss...")
    random.seed(42)  # Ensure repeatability of packet loss simulation
    client = Client("127.0.0.1", 12345, loss_probability=0.3)
    client.run(data_list, 'with_loss.csv', 'latency_with_loss.csv')
    
    print("Execution completed.")
