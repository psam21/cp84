
# Transaction Fee API Endpoints (No Auth Required)

This document lists publicly accessible, free API endpoints for fetching current transaction fees for **Bitcoin (BTC)**, **Ethereum (ETH)**, and **BNB Smart Chain (BNB)**.

---

## ✅ Bitcoin (BTC) Fee Estimates

**Endpoint:**  
```
btc: https://mempool.space/api/v1/fees/recommended
```  

**Description:**  
Returns low/medium/high sats/vB fee rates from mempool.space’s REST API. No authentication required.

---

## ✅ Ethereum (ETH) Gas Price Estimation

**Endpoint:**  
```
eth: https://api.etherscan.io/api?module=gastracker&action=gasoracle
```  

**Description:**  
Returns Safe/Propose/Fast gas prices in Gwei. Etherscan public endpoint for gas oracle data. No API key needed for basic access.

---

## ✅ BNB Smart Chain (BNB) Gas Price

**Endpoint (RPC):**  
```
bnb: https://bsc-dataseed.binance.org
```  

**Alternative RPC (DRPC):**  
```
bnb: https://bsc.drpc.org
```  

**JSON-RPC Payload:**  
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "eth_gasPrice",
  "params": []
}
```  

**Description:**  
Returns current gas price in Wei via standard JSON-RPC `eth_gasPrice` method. Works on most public nodes.

---

## 📊 Summary Table

| Chain | Endpoint | Description |
|-------|----------|-------------|
| **btc** | `https://mempool.space/api/v1/fees/recommended` | Sats/vB fee recommendations |
| **eth** | `https://api.etherscan.io/api?module=gastracker&action=gasoracle` | Safe/Propose/Fast Gwei rates |
| **bnb** | *RPC endpoint* (e.g., `https://bsc-dataseed.binance.org`) | JSON-RPC call `eth_gasPrice` returns Wei |

---

## 🛠️ Usage Examples

**BTC (curl)**  
```bash
curl https://mempool.space/api/v1/fees/recommended
```

**ETH (curl)**  
```bash
curl "https://api.etherscan.io/api?module=gastracker&action=gasoracle"
```

**BNB (curl)**  
```bash
curl -X POST https://bsc.drpc.org \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"eth_gasPrice","params":[]}'
```

---
