#!/usr/bin/env python3
"""
metrics_rpc.py

Mede o tempo de resposta das chamadas RPC para um nó Hyperledger Besu e
gera estatísticas (avg, median, p50, p95, p99, min, max, success rate).
Opcionalmente salva um CSV com os tempos individuais.

Uso:
    python3 metrics_rpc.py [--url URL] [--requests N] [--concurrency C]
                           [--timeout S] [--csv arquivo.csv] [--payload METHOD]

Exemplos:
    python3 metrics_rpc.py --requests 200 --concurrency 20
    python3 metrics_rpc.py --url http://192.168.1.10:8545 --requests 1000 --concurrency 50 --csv resultados.csv
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import time
import statistics
import argparse
import csv
import sys

DEFAULT_URL = "http://127.0.0.1:8545"
DEFAULT_REQUESTS = 500
DEFAULT_CONCURRENCY = 50
DEFAULT_TIMEOUT = 5.0

def make_payload(method_name: str):
    """Retorna um payload JSON-RPC simples para o método desejado."""
    # Métodos leves recomendados para medir latência: eth_blockNumber, net_version
    return {"jsonrpc": "2.0", "method": method_name, "params": [], "id": 1}

def single_request(session: requests.Session, url: str, payload: dict, timeout: float):
    """
    Executa uma requisição POST e retorna (elapsed_seconds, status_code, error_string_or_empty).
    """
    start = time.perf_counter()
    try:
        resp = session.post(url, json=payload, timeout=timeout)
        elapsed = time.perf_counter() - start
        return elapsed, resp.status_code, ""
    except Exception as e:
        elapsed = time.perf_counter() - start
        return elapsed, None, str(e)

def measure(url: str, total: int, concurrency: int, timeout: float, payload: dict, csv_out: str = None):
    """
    Realiza 'total' requisições ao 'url' com 'concurrency' threads e retorna estatísticas.
    """
    times = []
    statuses = []
    errors = []

    session = requests.Session()
    # Ajuste de headers comum para RPC
    session.headers.update({"Content-Type": "application/json"})

    start_all = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as ex:
        futures = [ex.submit(single_request, session, url, payload, timeout) for _ in range(total)]
        completed = 0
        for fut in as_completed(futures):
            elapsed, status, err = fut.result()
            times.append(elapsed)
            statuses.append(status)
            errors.append(err)
            completed += 1
            # feedback mínimo no console
            if completed % max(1, total // 10) == 0:
                print(f"[{completed}/{total}] requisições completadas", file=sys.stderr)

    total_time = time.perf_counter() - start_all
    # Estatísticas básicas (filtrando apenas respostas bem sucedidas para alguns cálculos)
    successful_times = [t for t, s in zip(times, statuses) if s is not None and 200 <= s < 300]

    stats = {}
    stats["total_requests"] = total
    stats["successful_requests"] = sum(1 for s in statuses if s is not None and 200 <= s < 300)
    stats["failed_requests"] = total - stats["successful_requests"]
    stats["success_rate"] = stats["successful_requests"] / total if total > 0 else 0.0
    stats["total_elapsed_s"] = total_time
    stats["reqs_per_sec"] = total / total_time if total_time > 0 else 0.0

    if successful_times:
        stats["avg_s"] = statistics.mean(successful_times)
        stats["median_s"] = statistics.median(successful_times)
        stats["min_s"] = min(successful_times)
        stats["max_s"] = max(successful_times)
        sorted_times = sorted(successful_times)
        def percentile(p):
            idx = int(len(sorted_times) * p / 100)
            idx = min(max(0, idx), len(sorted_times)-1)
            return sorted_times[idx]
        stats["p50_s"] = percentile(50)
        stats["p95_s"] = percentile(95)
        stats["p99_s"] = percentile(99)
    else:
        stats.update({k: None for k in ["avg_s","median_s","min_s","max_s","p50_s","p95_s","p99_s"]})

    # Salva CSV com tempos individuais se requerido
    if csv_out:
        with open(csv_out, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["index", "elapsed_s", "status_code", "error"])
            for i, (t, s, e) in enumerate(zip(times, statuses, errors), start=1):
                writer.writerow([i, f"{t:.6f}", s if s is not None else "", e])
        print(f"CSV salvo em: {csv_out}")

    return stats

def print_stats(stats: dict):
    print("\n===== RESULTADO =====")
    print(f"Requisições totais:      {stats['total_requests']}")
    print(f"Requisições bem-sucedidas: {stats['successful_requests']}")
    print(f"Requisições falhas:       {stats['failed_requests']}")
    print(f"Taxa de sucesso:         {stats['success_rate']*100:.2f}%")
    print(f"Total tempo (s):         {stats['total_elapsed_s']:.3f}")
    print(f"Throughput (req/s):      {stats['reqs_per_sec']:.2f}")
    if stats["avg_s"] is not None:
        print(f"Tempo médio (s):         {stats['avg_s']:.4f}")
        print(f"Mediana (s):             {stats['median_s']:.4f}")
        print(f"p50 (s):                 {stats['p50_s']:.4f}")
        print(f"p95 (s):                 {stats['p95_s']:.4f}")
        print(f"p99 (s):                 {stats['p99_s']:.4f}")
        print(f"Min (s):                 {stats['min_s']:.4f}")
        print(f"Max (s):                 {stats['max_s']:.4f}")
    else:
        print("Nenhuma requisição bem-sucedida para calcular estatísticas de latência.")

def parse_args():
    p = argparse.ArgumentParser(description="Mede tempo médio RPC de um nó Besu")
    p.add_argument("--url", type=str, default=DEFAULT_URL, help=f"URL do RPC (default: {DEFAULT_URL})")
    p.add_argument("--requests", type=int, default=DEFAULT_REQUESTS, help=f"Número total de requisições (default: {DEFAULT_REQUESTS})")
    p.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY, help=f"Concorrência (threads) (default: {DEFAULT_CONCURRENCY})")
    p.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, help=f"Timeout por requisição (s) (default: {DEFAULT_TIMEOUT})")
    p.add_argument("--csv", type=str, default=None, help="Salvar resultados individuais em CSV (ex: resultados.csv)")
    p.add_argument("--method", type=str, default="eth_blockNumber", help="Método RPC a usar no payload (default: eth_blockNumber)")
    return p.parse_args()

def main():
    args = parse_args()
    payload = make_payload(args.method)
    print(f"Medição: url={args.url} requests={args.requests} concurrency={args.concurrency} timeout={args.timeout} method={args.method}")
    stats = measure(args.url, args.requests, args.concurrency, args.timeout, payload, csv_out=args.csv)
    print_stats(stats)

if __name__ == "__main__":
    main()
