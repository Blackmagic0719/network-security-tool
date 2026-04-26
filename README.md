# BLACKMAGICK v3.0 — Advanced Network Recon Engine

```
  ██████╗ ██╗      █████╗  ██████╗██╗  ██╗    ███╗   ███╗ █████╗  ██████╗ ██╗ ██████╗██╗  ██╗
  ...
```

A powerful CLI-based network security and reconnaissance tool for authorized use on
networks you own or have explicit permission to test.

---

## Features

| Feature                | Description                                              |
|------------------------|----------------------------------------------------------|
| Network Discovery      | ICMP + TCP probe sweep of entire /24 subnet              |
| Port Scanning          | Common ports, full 1–65535 scan, or slow stealth mode    |
| Banner Grabbing        | Pulls service version banners from open ports            |
| OS Fingerprinting      | TTL-based + open port heuristic OS detection             |
| Service Detection      | Maps ports to service names (55+ services)               |
| DNS Recon              | A, MX, NS, TXT, CNAME, AAAA records via dig/nslookup     |
| WHOIS Lookup           | Domain/IP registry info via system whois                 |
| Traceroute             | Hop-by-hop path mapping with RTT display                 |
| CVE / Vuln Hints       | Matches service+version against known CVE database       |
| Session Export         | Full JSON report export with timestamps                  |
| Hacker UI              | Green-on-black terminal aesthetic with glitch effects    |

---

## Installation

```bash
pip install colorama
```

---

## Usage

```bash
python main.py
```

### Commands

```
scan network          Discover all live hosts on your /24 subnet
scan <ip>             Port scan with common ports
scan <ip> full        Full scan ports 1–65535
scan <ip> stealth     Slow, low-noise scan
os <ip>               OS fingerprint via TTL analysis
banner <ip> <port>    Grab raw service banner
dns <domain>          DNS recon (A/MX/NS/TXT/CNAME)
whois <target>        WHOIS lookup for domain or IP
trace <ip>            Traceroute with RTT per hop
vuln <ip>             CVE hint check against open services
export                Save session results to JSON file
history               Show all scans in current session
clear                 Redraw banner
exit                  End session (auto-exports if data exists)
```

---

## Legal Notice

> This tool is for **authorized security testing and education only**.
> Only use on networks and systems you own or have explicit written permission to test.
> Unauthorized scanning may violate computer crime laws in your jurisdiction.
