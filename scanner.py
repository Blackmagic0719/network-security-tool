"""
scanner.py - BLACKMAGICK v3.0 Backend Engine
Advanced network reconnaissance and security analysis
"""

import os
import socket
import struct
import time
import random
import platform
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

# ─── Service name map ────────────────────────────────────────────────────────
SERVICE_MAP = {
    20: "FTP-DATA", 21: "FTP", 22: "SSH", 23: "TELNET",
    25: "SMTP", 53: "DNS", 67: "DHCP", 68: "DHCP",
    80: "HTTP", 110: "POP3", 111: "RPCBIND", 119: "NNTP",
    123: "NTP", 135: "MSRPC", 137: "NETBIOS-NS", 138: "NETBIOS-DGM",
    139: "NETBIOS-SSN", 143: "IMAP", 161: "SNMP", 162: "SNMP-TRAP",
    179: "BGP", 194: "IRC", 389: "LDAP", 443: "HTTPS",
    445: "SMB", 465: "SMTPS", 514: "SYSLOG", 515: "LPD",
    587: "SMTP-SUBMIT", 631: "IPP", 636: "LDAPS", 989: "FTPS-DATA",
    990: "FTPS", 993: "IMAPS", 995: "POP3S", 1080: "SOCKS",
    1194: "OPENVPN", 1433: "MSSQL", 1521: "ORACLE", 1723: "PPTP",
    2049: "NFS", 2082: "CPANEL", 2083: "CPANEL-SSL", 2222: "SSH-ALT",
    3000: "DEV-SERVER", 3306: "MYSQL", 3389: "RDP", 4000: "ICQ",
    4444: "METASPLOIT", 5000: "UPnP", 5432: "POSTGRESQL",
    5900: "VNC", 5985: "WINRM", 6379: "REDIS", 6667: "IRC",
    7070: "REALSERVER", 8000: "HTTP-ALT", 8008: "HTTP-ALT",
    8080: "HTTP-PROXY", 8443: "HTTPS-ALT", 8888: "JUPYTER",
    9000: "FASTCGI", 9090: "ZEUS-ADMIN", 9200: "ELASTICSEARCH",
    9300: "ELASTICSEARCH", 27017: "MONGODB", 27018: "MONGODB",
}

COMMON_PORTS = [
    21, 22, 23, 25, 53, 67, 68, 80, 110, 111, 123, 135,
    137, 138, 139, 143, 161, 389, 443, 445, 465, 514, 587,
    631, 636, 993, 995, 1080, 1433, 1521, 1723, 2049, 2082,
    2083, 2222, 3000, 3306, 3389, 4444, 5432, 5900, 5985,
    6379, 6667, 7070, 8000, 8008, 8080, 8443, 8888, 9000,
    9090, 9200, 27017
]

# ─── CVE / Vulnerability hint database ──────────────────────────────────────
VULN_DB = {
    "SSH": [
        ("openssh 7", "CVE-2023-38408 – Agent remote code execution (OpenSSH < 9.3p2)"),
        ("openssh 8", "CVE-2023-51385 – ProxyCommand argument injection"),
        ("dropbear",  "CVE-2020-36254 – Buffer overflow in Dropbear SSH < 2020.80"),
    ],
    "HTTP": [
        ("apache/2.4.4", "CVE-2021-41773 – Path traversal & RCE (Apache 2.4.49)"),
        ("apache/2.4.5", "CVE-2021-42013 – Path traversal (Apache 2.4.49/50)"),
        ("nginx/1.14",   "CVE-2019-9511 – HTTP/2 DoS (NGINX < 1.17.3)"),
        ("iis/7",        "CVE-2017-7269 – IIS 6.0 WebDAV buffer overflow"),
    ],
    "FTP": [
        ("vsftpd 2.3.4", "CVE-2011-2523 – VSFTPD 2.3.4 backdoor RCE"),
        ("proftpd 1.3",  "CVE-2019-12815 – ProFTPD mod_copy unauthenticated file copy"),
        ("filezilla",    "CVE-2021-3492 – Potential privilege escalation"),
    ],
    "SMB": [
        ("",             "CVE-2017-0144 – EternalBlue / MS17-010 (WannaCry vector)"),
        ("",             "CVE-2020-0796 – SMBGhost RCE (Windows 10 / SMBv3.1.1)"),
        ("",             "CVE-2021-36942 – PetitPotam NTLM relay"),
    ],
    "RDP": [
        ("",             "CVE-2019-0708 – BlueKeep RCE (Windows 7/Server 2008)"),
        ("",             "CVE-2019-1182 – DejaBlue RCE (Windows 8–10 / Server 2012–2019)"),
    ],
    "MYSQL": [
        ("",             "CVE-2016-6662 – MySQL RCE via malicious my.cnf"),
        ("",             "CVE-2012-2122 – Authentication bypass (MariaDB / MySQL)"),
    ],
    "REDIS": [
        ("",             "CVE-2022-0543 – Sandbox escape via Lua scripting (Redis < 6.2.6)"),
        ("",             "Redis misconfiguration: no-auth often leads to full data exposure"),
    ],
    "TELNET": [
        ("",             "Cleartext protocol – credentials transmitted unencrypted"),
        ("",             "CVE-2011-4862 – FreeBSD telnetd encryption option buffer overflow"),
    ],
    "MONGODB": [
        ("",             "No authentication required by default in older versions"),
        ("",             "CVE-2021-20328 – SRV connection string injection"),
    ],
    "ELASTICSEARCH": [
        ("",             "No authentication in open deployments – data exposed"),
        ("",             "CVE-2021-22144 – Slowloris DoS via malformed HTTP"),
    ],
    "VNC": [
        ("",             "CVE-2019-15681 – LibVNC memory disclosure"),
        ("",             "Brute-forceable if no lockout policy configured"),
    ],
}

# ─── IP / Network helpers ────────────────────────────────────────────────────
def get_base_ip():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        local_ip = sock.getsockname()[0]
        sock.close()
    except Exception:
        local_ip = socket.gethostbyname(socket.gethostname())
    return ".".join(local_ip.split(".")[:-1])

# ─── Banner grabbing ─────────────────────────────────────────────────────────
def grab_banner(ip, port, timeout=1.5):
    probes = {
        80:  b"HEAD / HTTP/1.1\r\nHost: {}\r\n\r\n".format(ip).encode() if not isinstance(ip, bytes) else b"HEAD / HTTP/1.1\r\n\r\n",
        21:  None,
        22:  None,
        25:  None,
        110: None,
        143: None,
    }
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))

        probe = probes.get(port)
        if probe:
            sock.sendall(probe)

        data = sock.recv(1024)
        sock.close()
        return data.decode("utf-8", errors="ignore").strip()[:120]
    except Exception:
        return None

def service_version_detect(ip, port):
    banner = grab_banner(ip, port)
    return banner or "No banner"

# ─── Port scanner ─────────────────────────────────────────────────────────────
def scan_port(ip, port, timeout=0.5):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        if result == 0:
            service = SERVICE_MAP.get(port, "UNKNOWN")
            banner  = grab_banner(ip, port, timeout=1.0)
            return (port, banner or "", service)
    except Exception:
        pass
    return None

def scan_ports(ip, port_range="common"):
    if port_range == "common":
        ports = COMMON_PORTS
    elif port_range == "full":
        ports = range(1, 65536)
    elif port_range == "stealth":
        ports = COMMON_PORTS
    else:
        ports = COMMON_PORTS

    open_ports = []
    workers = 200 if port_range == "full" else 100
    timeout  = 1.5 if port_range == "stealth" else 0.5

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(scan_port, ip, p, timeout): p for p in ports}
        for fut in as_completed(futures):
            res = fut.result()
            if res:
                open_ports.append(res)

    open_ports.sort(key=lambda x: x[0])
    return open_ports

# ─── OS Fingerprinting ───────────────────────────────────────────────────────
def os_fingerprint(ip):
    """
    Heuristic OS detection via ICMP TTL and open port signatures.
    Real Nmap-style fingerprinting requires raw sockets (root).
    This provides a best-effort estimate.
    """
    try:
        param = "-n" if platform.system().lower() == "windows" else "-c"
        cmd   = ["ping", param, "1", ip]
        out   = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=3).decode()

        ttl = None
        for word in out.split():
            if "ttl=" in word.lower():
                try:
                    ttl = int(word.split("=")[1])
                except Exception:
                    pass

        if ttl is None:
            return {"os": "Unreachable / Filtered", "ttl": "N/A", "window": "N/A", "confidence": 0}

        if ttl <= 64:
            os_guess = "Linux / Android / macOS / Unix"
            confidence = 75
        elif ttl <= 128:
            os_guess = "Windows (NT/2000/XP/7/10/11)"
            confidence = 80
        elif ttl <= 255:
            os_guess = "Cisco IOS / Network Device"
            confidence = 70
        else:
            os_guess = "Unknown"
            confidence = 30

        # Refine by open ports
        try:
            open_p = [r[0] for r in scan_ports(ip, "common")]
            if 3389 in open_p:
                os_guess = "Windows (RDP enabled)"
                confidence = min(95, confidence + 15)
            if 22 in open_p and 80 not in open_p:
                os_guess += " – likely server"
            if 445 in open_p:
                os_guess = "Windows (SMB exposed)"
                confidence = min(95, confidence + 10)
        except Exception:
            pass

        return {"os": os_guess, "ttl": ttl, "window": "N/A (raw sockets required)", "confidence": confidence}

    except Exception as e:
        return {"os": f"Detection failed: {e}", "ttl": "N/A", "window": "N/A", "confidence": 0}

# ─── Vulnerability hints ─────────────────────────────────────────────────────
def vuln_hints(service, version_str):
    hints = []
    version_lower = version_str.lower()
    svc = service.upper()

    entries = VULN_DB.get(svc, [])
    for keyword, cve in entries:
        if not keyword or keyword.lower() in version_lower:
            hints.append(cve)

    # Generic high-risk flags
    if svc == "TELNET":
        hints.append("CRITICAL: Telnet transmits credentials in plaintext")
    if svc in ("FTP", "FTP-DATA") and "sftp" not in version_lower:
        hints.append("WARNING: Plain FTP – credentials transmitted unencrypted")
    if svc == "REDIS" and not version_lower:
        hints.append("WARNING: Redis open on network – check authentication config")

    return hints[:5]  # cap at 5 hints per service

# ─── DNS Reconnaissance ──────────────────────────────────────────────────────
def dns_recon(domain):
    """
    DNS recon using socket + subprocess dig/nslookup as fallback.
    No dnspython dependency required.
    """
    records = {}

    # A record
    try:
        a = socket.gethostbyname_ex(domain)
        records["A"] = a[2]
    except Exception:
        records["A"] = ["Lookup failed"]

    # Attempt dig for additional records
    for rtype in ["MX", "NS", "TXT", "CNAME", "AAAA"]:
        try:
            result = subprocess.check_output(
                ["dig", "+short", rtype, domain],
                stderr=subprocess.DEVNULL, timeout=5
            ).decode().strip()
            if result:
                records[rtype] = [l.strip() for l in result.split("\n") if l.strip()]
        except Exception:
            pass

    # Fallback: nslookup
    if len(records) <= 1:
        try:
            out = subprocess.check_output(
                ["nslookup", domain], stderr=subprocess.DEVNULL, timeout=5
            ).decode()
            for line in out.split("\n"):
                if "Address:" in line and "#" not in line:
                    records.setdefault("A-NS", []).append(line.split("Address:")[-1].strip())
        except Exception:
            pass

    return records

# ─── WHOIS ────────────────────────────────────────────────────────────────────
def whois_lookup(target):
    """
    WHOIS via system whois command.
    """
    data = {}
    try:
        out = subprocess.check_output(
            ["whois", target], stderr=subprocess.DEVNULL, timeout=10
        ).decode(errors="ignore")

        fields = {
            "Registrar":      ["Registrar:", "registrar:"],
            "Created":        ["Creation Date:", "created:", "Registered:"],
            "Expires":        ["Registry Expiry Date:", "Expiry Date:", "expires:"],
            "Updated":        ["Updated Date:", "last-modified:"],
            "Name Servers":   ["Name Server:", "nserver:"],
            "Registrant Org": ["Registrant Organization:", "org-name:"],
            "Country":        ["Registrant Country:", "country:"],
            "Abuse Email":    ["Abuse Email:", "abuse-mailbox:"],
        }

        for label, keys in fields.items():
            for key in keys:
                for line in out.split("\n"):
                    if line.strip().lower().startswith(key.lower()):
                        val = line.split(":", 1)[-1].strip()
                        if val and label not in data:
                            data[label] = val
                        break

        if not data:
            data["Raw (first 500 chars)"] = out[:500].replace("\n", " | ")

    except FileNotFoundError:
        data["Error"] = "'whois' command not found on this system"
    except Exception as e:
        data["Error"] = str(e)

    return data

# ─── Traceroute ───────────────────────────────────────────────────────────────
def traceroute(ip, max_hops=20):
    hops = []
    is_win = platform.system().lower() == "windows"
    cmd = ["tracert", "-d", "-h", str(max_hops), ip] if is_win else \
          ["traceroute", "-n", "-m", str(max_hops), ip]
    try:
        out = subprocess.check_output(
            cmd, stderr=subprocess.DEVNULL, timeout=60
        ).decode(errors="ignore")

        for line in out.split("\n"):
            line = line.strip()
            if not line or "traceroute" in line.lower() or "tracing" in line.lower():
                continue
            parts = line.split()
            if not parts or not parts[0].isdigit():
                continue
            hop_ip = None
            rtt = None
            for p in parts[1:]:
                if "." in p or ":" in p:
                    try:
                        socket.inet_aton(p)
                        hop_ip = p
                    except Exception:
                        pass
                elif "ms" in p.lower():
                    try:
                        rtt = float(parts[parts.index(p) - 1])
                    except Exception:
                        pass
            if not hop_ip:
                hop_ip = "*"
            if rtt is None:
                rtt = -1
            hops.append({"hop": int(parts[0]), "ip": hop_ip, "hostname": hop_ip, "rtt": rtt})

    except FileNotFoundError:
        hops = [{"hop": 1, "ip": "N/A", "hostname": "traceroute not available", "rtt": -1}]
    except subprocess.TimeoutExpired:
        hops.append({"hop": "?", "ip": "TIMEOUT", "hostname": "", "rtt": -1})
    except Exception as e:
        hops = [{"hop": 1, "ip": "ERROR", "hostname": str(e), "rtt": -1}]

    return hops

# ─── Network scan (ping sweep) ───────────────────────────────────────────────
def _ping(ip):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    extra = ["-W", "1"] if platform.system().lower() != "windows" else []
    cmd = ["ping", param, "1"] + extra + [ip]
    try:
        return subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2) == 0
    except Exception:
        return False

def scan_network(base_ip, cb=None):
    def probe(i):
        ip = f"{base_ip}.{i}"
        if _ping(ip):
            ports = scan_ports(ip, "common")
            if cb:
                cb(ip, ports)
            return (ip, ports)
        return None

    with ThreadPoolExecutor(max_workers=50) as ex:
        results = list(ex.map(probe, range(1, 255)))

    return [r for r in results if r]
