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