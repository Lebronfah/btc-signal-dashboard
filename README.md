# BTC 5-Minute Signal Desk

A research-only, mobile-friendly Flask website. Connects to Coinbase spot, Polymarket Gamma, CLOB order books, and public trade history. Ranks **observable wallet addresses in the current round**, not purported named whales. No invented social-media sentiment. The model is a simple, unvalidated short-term volatility estimate, not a proven strategy.

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Visit http://localhost:8080 (or the host computer's LAN IP on your phone). It needs a persistent Python server. Deploy this folder to a Python-capable hosting provider for a public URL; this package itself is not hosted. A free service that sleeps may not run continuously.

## Limitations

- Coinbase BTC/USD spot is **not** the Chainlink 60-second TWAP that determines Polymarket settlement.
- The model is not backtested or calibrated; it uses an arbitrary conservative edge threshold and cost buffer, not actual verified taker fees.
- Price observations are collected only while the server receives requests; no reliable full-round start price exists if polling begins after the boundary.
- Whale activity is limited to public recent trades in the current round. It does not identify the biggest Bitcoin traders globally or prove whether a wallet is net long or short.
- X, YouTube Live and TikTok commentary require separately authorized API integrations; they are not included. The interface explicitly shows them as unconnected.
- No orders are placed; no unattended 24/7 operation or 9:00 AM automatic start is guaranteed until deployed with a suitable always-on server and scheduler.
