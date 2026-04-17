import socket
from colorama import Fore

def scan_ports(target):
    print(Fore.YELLOW + f"\n[+] Scanning ports on {target}...\n")

    for port in range(1, 1025):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.3)

        result = sock.connect_ex((target, port))

        if result == 0:
            print(Fore.GREEN + f"[OPEN] Port {port}")

        sock.close()