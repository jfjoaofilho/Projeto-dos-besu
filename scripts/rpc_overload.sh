#!/bin/bash
for i in {1..1000}
do
  curl -s -X POST http://127.0.0.1:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":["latest", true],"id":1}' &
done
