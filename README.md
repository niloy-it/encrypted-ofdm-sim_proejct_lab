<div align="center">

# 🔐 Encrypted-OFDM Simulation

**Physical Layer Security for Wireless Communications**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Paper](https://img.shields.io/badge/Paper-Elsevier%202024-orange.svg)](https://doi.org/10.1016/j.comnet.2024.110182)

*A Python implementation demonstrating how Encrypted-OFDM provides 
physical layer security against eavesdroppers*

[📖 Background](#background) • 
[🚀 Quick Start](#quick-start) • 
[📊 Results](#results) • 
[🔬 How It Works](#how-it-works)

</div>

---

## 📖 Background

This simulation is inspired by:

> **Mohammed & Saha, "Encrypted-OFDM: A Secured Wireless Waveform"**  
> *Elsevier Computer Networks, 2024*

### The Problem
Traditional OFDM (used in WiFi, LTE, 5G) transmits data that any receiver 
can potentially intercept and decode.

### The Solution
Encrypted-OFDM adds physical layer encryption that:
- ✅ Allows **legitimate receivers** (with key) to decode normally
- ❌ Forces **eavesdroppers** (without key) to see only noise

---

## 🚀 Quick Start

### Option 1: Run Locally

```bash
# Clone this repository
git clone https://github.com/niloy-it/encrypted-ofdm-sim.git
cd encrypted-ofdm-sim

# Install dependencies
pip install -r requirements.txt

# Run simulation
python encrypted_ofdm.py
