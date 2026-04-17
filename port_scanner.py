import socket
from colorama import Fore
from concurrent.futures import ThreadPoolExecutor

open_ports = []

def scan_port(target, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.3)

        result = sock.connect_ex((target, port))
        if result == 0:
            open_ports.append(port)
            print(Fore.GREEN + f"[OPEN] Port {port}")

        sock.close()
    except:
        pass


def scan_ports(target):
    print(Fore.YELLOW + f"\n[+] Scanning {target} with EVIL engine...\n")

    ports = range(1, 1025)

    # 🔥 Multithreading (FAST)
    with ThreadPoolExecutor(max_workers=100) as executor:
        for port in ports:
            executor.submit(scan_port, target, port)

    print(Fore.RED + "\n[SCAN COMPLETE]")
    print(Fore.CYAN + f"Open Ports: {open_ports}\n")