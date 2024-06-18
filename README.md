- pip install -r requirements.txt;
- Execute o Servidor.py;
- Execute o Cliente.py, serão trafegados 1000 pacotes para análise dos parâmetros e geração dos gráficos utilizados na análise;
  Como podemos observar são gerados os arquivos csv's com os dados que serão utilizados na plotagem dos gráficos
- Execute o arquivo plotar.py para que sejam exibidos os gráficos de acordo com as definições;
- O parâmetro de perda de pacotes pode ser ajustado no run do cliente;
Um exemplo é definir o loss_probability do cliente para 0.3 e 0.1 conforme gráficos gerados no relatório, com essas probailidades de perdas podemos observar o comportamento do protocolo desenvolvido.
