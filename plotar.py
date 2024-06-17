import matplotlib.pyplot as plt
import pandas as pd

# Carregar dados dos arquivos CSV
latency_without_loss = pd.read_csv('latency_without_loss.csv')
latency_with_loss = pd.read_csv('latency_with_loss.csv')
throughput_without_loss = pd.read_csv('without_loss.csv')
throughput_with_loss = pd.read_csv('with_loss.csv')

# Criar uma figura com dois subgráficos
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))

# Subgráfico de Latência
ax1.plot(latency_without_loss['seq_num'], latency_without_loss['latency'], label='Sem Perda', marker='o', linestyle='-', color='b')
ax1.plot(latency_with_loss['seq_num'], latency_with_loss['latency'], label='Com Perda', marker='o', linestyle='-', color='r')
ax1.set_xlabel('Número de Sequência do Pacote')
ax1.set_ylabel('Latência (segundos)')
ax1.set_title('Latência dos Pacotes ao Longo do Tempo')
ax1.legend()
ax1.grid(True)

# Subgráfico de Vazão
ax2.plot(throughput_without_loss['num_packets'], throughput_without_loss['throughput'], label='Sem Perda', marker='o', linestyle='-', color='b')
ax2.plot(throughput_with_loss['num_packets'], throughput_with_loss['throughput'], label='Com Perda', marker='o', linestyle='-', color='r')
ax2.set_xlabel('Número de Pacotes')
ax2.set_ylabel('Vazão (pacotes/segundo)')
ax2.set_title('Vazão da Rede para o Envio de 1000 Pacotes')
ax2.legend()
ax2.grid(True)

# Ajustar layout
plt.tight_layout()
plt.savefig('latency_throughput_comparison.png')
plt.show()
