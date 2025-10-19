import requests, time, statistics

url = "http://localhost:8545"
payload = {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}

tempos = []
for _ in range(30):
    inicio = time.time()
    requests.post(url, json=payload)
    tempos.append(time.time() - inicio)

print(f"Tempo médio de resposta RPC: {statistics.mean(tempos):.3f} segundos")