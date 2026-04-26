#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════╗
║         BLACKMAGICK v3.0 - ADVANCED RECON ENGINE      ║
║         Network Security & Intelligence Tool          ║
╚═══════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import json
import datetime
from colorama import Fore, Back, Style, init

try:
    from scanner import (
        scan_network, scan_ports, get_base_ip,
        os_fingerprint, whois_lookup, traceroute,
        dns_recon, service_version_detect, vuln_hints
    )
except ImportError:
    def get_base_ip(): return "192.168.1"
    def scan_network(ip, cb=None): pass
    def scan_ports(ip, port_range="common"): return [(80, "Apache/2.4.41", "HTTP")]
    def os_fingerprint(ip): return "Unknown"
    def whois_lookup(target): return {}
    def traceroute(ip): return []
    def dns_recon(domain): return {}
    def service_version_detect(ip, port): return "Unknown"
    def vuln_hints(service, version): return []

init(autoreset=True)

SESSION_START = datetime.datetime.now()
SCAN_LOG = []

# ─── Color shortcuts ────────────────────────────────────────────────────────
G  = Fore.GREEN
LG = Fore.LIGHTGREEN_EX
R  = Fore.RED
LR = Fore.LIGHTRED_EX
Y  = Fore.YELLOW
LY = Fore.LIGHTYELLOW_EX
C  = Fore.CYAN
LC = Fore.LIGHTCYAN_EX
M  = Fore.MAGENTA
LM = Fore.LIGHTMAGENTA_EX
W  = Fore.WHITE
DW = Fore.LIGHTBLACK_EX
B  = Style.BRIGHT
RS = Style.RESET_ALL

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def typewriter(text, delay=0.018, color=""):
    for ch in text:
        sys.stdout.write(color + ch)
        sys.stdout.flush()
        time.sleep(delay)
    print(RS)

def glitch_effect(text, color=G):
    glitch_chars = ["█", "▓", "▒", "░", "▄", "▀"]
    import random
    line = ""
    for ch in text:
        if random.random() < 0.06:
            line += color + random.choice(glitch_chars)
        else:
            line += color + ch
    print(line + RS)

def progress_bar(label, total=30, color=G):
    sys.stdout.write(f"  {color}{label:.<35}{RS} [")
    for i in range(total):
        time.sleep(0.03)
        sys.stdout.write(G + "█")
        sys.stdout.flush()
    print(G + "] " + LG + "DONE" + RS)

def display_banner():
    clear()
    banner = r"""
  ██████╗ ██╗      █████╗  ██████╗██╗  ██╗    ███╗   ███╗ █████╗  ██████╗ ██╗ ██████╗██╗  ██╗
  ██╔══██╗██║     ██╔══██╗██╔════╝██║ ██╔╝    ████╗ ████║██╔══██╗██╔════╝ ██║██╔════╝██║ ██╔╝
  ██████╔╝██║     ███████║██║     █████╔╝     ██╔████╔██║███████║██║  ███╗██║██║     █████╔╝
  ██╔══██╗██║     ██╔══██║██║     ██╔═██╗     ██║╚██╔╝██║██╔══██║██║   ██║██║██║     ██╔═██╗
  ██████╔╝███████╗██║  ██║╚██████╗██║  ██╗    ██║ ╚═╝ ██║██║  ██║╚██████╔╝██║╚██████╗██║  ██╗
  ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝   ╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝ ╚═════╝╚═╝  ╚═╝
"""
    for line in banner.split("\n"):
        glitch_effect(line, G)
        time.sleep(0.04)

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    base_ip = get_base_ip()

    print(DW + "  " + "─"*90)
    print(f"  {G}► VERSION   {W}v3.0-ADVANCED          {G}► SESSION   {W}{now}")
    print(f"  {G}► ENGINE    {W}BLACKMAGICK RECON       {G}► NETWORK   {W}{base_ip}.0/24")
    print(f"  {G}► STATUS    {LG}ONLINE {G}●               {G}► OPERATOR  {W}UNKNOWN")
    print(DW + "  " + "─"*90)
    print(f"\n  {DW}Type {G}'help'{DW} for command list  |  {DW}Type {G}'menu'{DW} for interactive menu\n")

def help_menu():
    cmds = [
        ("scan network",        "Discover all live hosts on your subnet"),
        ("scan <ip>",           "Port scan a single target (common ports)"),
        ("scan <ip> full",      "Full port scan 1–65535"),
        ("scan <ip> stealth",   "Stealth SYN-style slow scan"),
        ("os <ip>",             "OS fingerprinting via TTL & TCP stack"),
        ("banner <ip> <port>",  "Grab service banner from specific port"),
        ("dns <domain>",        "DNS reconnaissance (A, MX, NS, TXT records)"),
        ("whois <target>",      "WHOIS lookup for domain or IP"),
        ("trace <ip>",          "Traceroute / hop analysis to target"),
        ("vuln <ip>",           "Check open ports for known CVE hints"),
        ("export",              "Export session results to JSON report"),
        ("history",             "Show scan history for this session"),
        ("clear",               "Clear the terminal"),
        ("exit",                "Terminate session"),
    ]

    print(f"\n  {G}╔{'═'*70}╗")
    print(f"  {G}║{'COMMAND REFERENCE':^70}║")
    print(f"  {G}╠{'═'*70}╣")
    for cmd, desc in cmds:
        print(f"  {G}║  {Y}{cmd:<30}{W}{desc:<38}{G}  ║")
    print(f"  {G}╚{'═'*70}╝\n")

def section_header(title):
    width = 60
    print(f"\n  {G}┌{'─'*width}┐")
    print(f"  {G}│  {LG}{title:<{width-2}}{G}│")
    print(f"  {G}└{'─'*width}┘")

def log_result(action, target, data):
    SCAN_LOG.append({
        "timestamp": datetime.datetime.now().isoformat(),
        "action": action,
        "target": target,
        "data": data
    })

def do_port_scan(target_ip, mode="common"):
    section_header(f"PORT SCAN ► {target_ip}  [{mode.upper()} MODE]")
    port_range = mode

    print(f"  {DW}Initiating scan engine...")
    progress_bar("Loading port vectors", 20)

    results = scan_ports(target_ip, port_range)

    if results:
        print(f"\n  {G}{'PORT':<8}{'STATE':<10}{'SERVICE':<20}{'BANNER/VERSION'}")
        print(f"  {DW}{'─'*70}")
        for port, banner, service in results:
            state_color = LG
            print(f"  {state_color}{port:<8}{G}OPEN{'':<6}{C}{service:<20}{Y}{banner or ''}")
            hints = vuln_hints(service, banner or "")
            for h in hints:
                print(f"  {DW}  └─ {R}[CVE HINT] {LR}{h}")
        log_result("port_scan", target_ip, results)
    else:
        print(f"\n  {R}  No open ports detected on {target_ip}")

    print(f"\n  {DW}Scan complete: {LG}{len(results)} open port(s) found\n")

def do_os_fingerprint(target_ip):
    section_header(f"OS FINGERPRINT ► {target_ip}")
    progress_bar("Probing TCP stack signatures", 25)
    result = os_fingerprint(target_ip)
    print(f"\n  {G}Detected OS   : {W}{result['os']}")
    print(f"  {G}TTL Value     : {W}{result['ttl']}")
    print(f"  {G}TCP Window    : {W}{result['window']}")
    print(f"  {G}Confidence    : {LY}{result['confidence']}%\n")
    log_result("os_fingerprint", target_ip, result)

def do_dns_recon(domain):
    section_header(f"DNS RECON ► {domain}")
    progress_bar("Querying DNS records", 20)
    records = dns_recon(domain)
    for rtype, values in records.items():
        print(f"  {G}{rtype:<10}{DW}{'─'*3} ", end="")
        if isinstance(values, list):
            print(f"{W}{', '.join(str(v) for v in values)}")
        else:
            print(f"{W}{values}")
    log_result("dns_recon", domain, records)
    print()

def do_whois(target):
    section_header(f"WHOIS LOOKUP ► {target}")
    progress_bar("Fetching registry data", 20)
    data = whois_lookup(target)
    for key, val in data.items():
        print(f"  {G}{key:<20}{W}{val}")
    log_result("whois", target, data)
    print()

def do_traceroute(target_ip):
    section_header(f"TRACEROUTE ► {target_ip}")
    progress_bar("Mapping network path", 25)
    hops = traceroute(target_ip)
    print(f"\n  {G}{'HOP':<6}{'IP':<20}{'HOSTNAME':<35}{'RTT'}")
    print(f"  {DW}{'─'*70}")
    for i, hop in enumerate(hops, 1):
        rtt_color = LG if hop['rtt'] < 20 else (Y if hop['rtt'] < 80 else LR)
        print(f"  {C}{i:<6}{W}{hop['ip']:<20}{DW}{hop.get('hostname','*'):<35}{rtt_color}{hop['rtt']} ms")
    log_result("traceroute", target_ip, hops)
    print()

def do_vuln_check(target_ip):
    section_header(f"VULNERABILITY HINTS ► {target_ip}")
    print(f"  {DW}Running port scan first...")
    results = scan_ports(target_ip, "common")
    print(f"\n  {Y}⚠  These are informational hints only – not confirmed exploits\n")
    found_any = False
    for port, banner, service in results:
        hints = vuln_hints(service, banner or "")
        if hints:
            found_any = True
            print(f"  {C}Port {port} / {service}:")
            for h in hints:
                print(f"    {R}[!] {LR}{h}")
            print()
    if not found_any:
        print(f"  {LG}No common vulnerability hints matched open services.\n")

def do_network_scan():
    base_ip = get_base_ip()
    section_header(f"NETWORK DISCOVERY ► {base_ip}.0/24")
    print(f"  {DW}Pinging 254 hosts (ICMP + TCP probes)...")
    print(f"  {DW}This may take a moment...\n")

    live_hosts = []

    def host_found(ip, ports):
        live_hosts.append(ip)
        print(f"  {LG}[+] {W}{ip:<20}", end="")
        if ports:
            port_list = ", ".join(str(p[0]) for p in ports)
            print(f"{G}PORTS: {C}{port_list}")
        else:
            print(f"{DW}(no common ports)")

    scan_network(base_ip, cb=host_found)

    print(f"\n  {DW}{'─'*60}")
    print(f"  {G}Scan complete: {LG}{len(live_hosts)} host(s) discovered\n")
    log_result("network_scan", base_ip, live_hosts)

def do_export():
    fname = f"blackmagick_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report = {
        "tool": "BLACKMAGICK v3.0",
        "session_start": SESSION_START.isoformat(),
        "session_end": datetime.datetime.now().isoformat(),
        "results": SCAN_LOG
    }
    with open(fname, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\n  {G}[+] Report exported: {LG}{fname}\n")

def do_history():
    if not SCAN_LOG:
        print(f"\n  {DW}No scans performed yet.\n")
        return
    section_header("SESSION HISTORY")
    for i, entry in enumerate(SCAN_LOG, 1):
        ts = entry['timestamp'].split("T")[1][:8]
        print(f"  {DW}{i:>3}.  {G}{ts}  {C}{entry['action']:<20}{W}{entry['target']}")
    print()

def do_banner_grab(ip, port):
    section_header(f"BANNER GRAB ► {ip}:{port}")
    result = service_version_detect(ip, int(port))
    print(f"  {G}Banner: {W}{result}\n")

def main_cli():
    display_banner()

    while True:
        try:
            prompt = (
                f"\n  {DW}[{G}{datetime.datetime.now().strftime('%H:%M:%S')}{DW}] "
                f"{G}root{DW}@{LG}blackmagick{DW}:{G}~{DW}$ {W}"
            )
            cmd = input(prompt).strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n  {R}[!] Interrupt signal received.")
            print(f"  {DW}Exporting session data...")
            if SCAN_LOG:
                do_export()
            print(f"  {G}Session terminated.\n")
            sys.exit(0)

        if not cmd:
            continue

        parts = cmd.lower().split()
        verb = parts[0]

        if verb == "help":
            help_menu()

        elif verb == "menu":
            help_menu()

        elif verb == "clear":
            display_banner()

        elif verb == "exit" or verb == "quit":
            print(f"\n  {R}[SYS] Terminating session...")
            time.sleep(0.5)
            if SCAN_LOG:
                do_export()
            print(f"  {G}Goodbye.\n")
            break

        elif verb == "history":
            do_history()

        elif verb == "export":
            do_export()

        elif cmd == "scan network":
            do_network_scan()

        elif verb == "scan" and len(parts) >= 2:
            target = parts[1]
            mode = parts[2] if len(parts) > 2 else "common"
            do_port_scan(target, mode)

        elif verb == "os" and len(parts) == 2:
            do_os_fingerprint(parts[1])

        elif verb == "dns" and len(parts) == 2:
            do_dns_recon(parts[1])

        elif verb == "whois" and len(parts) == 2:
            do_whois(parts[1])

        elif verb == "trace" and len(parts) == 2:
            do_traceroute(parts[1])

        elif verb == "vuln" and len(parts) == 2:
            do_vuln_check(parts[1])

        elif verb == "banner" and len(parts) == 3:
            do_banner_grab(parts[1], parts[2])

        else:
            print(f"  {R}[!] Unknown command: {W}{cmd}{DW}  (type 'help' for commands)")


if __name__ == "__main__":
    main_cli()
