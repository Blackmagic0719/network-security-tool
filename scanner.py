import os
import socket
from colorama import Fore

# 🔍 Auto detect base IP
def get_base_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return ".".join(local_ip.split('.')[:-1])


# 📡 Ping check
def ping(ip):
    return os.system(f"ping -n 1 {ip} > nul") == 0


# 🧠 Banner grabbing
def grab_banner(ip, port):
    try:
        sock = socket.socket()
        sock.settimeout(1)
        sock.connect((ip, port))
        banner = sock.recv(1024).decode().strip()
        sock.close()
        return banner
    except:
        return None


# 🚪 Port scanning
from concurrent.futures import ThreadPoolExecutor
import socket

def scan_port(ip, port):
    try:
        sock = socket.socket()
        sock.settimeout(0.5)
        result = sock.connect_ex((ip, port))

        if result == 0:
            banner = grab_banner(ip, port)
            return (port, banner)

        sock.close()
    except:
        pass

    return None


def scan_ports(ip):
    common_ports = [21, 22, 23, 53, 80, 139, 443, 445]
    open_ports = []

    with ThreadPoolExecutor(max_workers=50) as executor:
        results = executor.map(lambda p: scan_port(ip, p), common_ports)

    for result in results:
        if result:
            open_ports.append(result)

    return open_ports


# 🌐 Main network scan
def scan_network(base_ip):
    print(Fore.YELLOW + "[+] Scanning network...\n")

    # clear previous results
    with open("scan_results.txt", "w") as f:
        f.write("=== BLACKMAGICK SCAN RESULTS ===\n\n")

    for i in range(1, 255):
        ip = f"{base_ip}.{i}"

        if ping(ip):
            ports = scan_ports(ip)

            print(Fore.GREEN + f"[ACTIVE] {ip}")

            with open("scan_results.txt", "a") as f:
                f.write(f"{ip}\n")

            if ports:
                for port, banner in ports:
                    print(Fore.CYAN + f"   Port {port} OPEN")

                    with open("scan_results.txt", "a") as f:
                        f.write(f"   Port {port} OPEN\n")

                    if banner:
                        print(Fore.YELLOW + f"      Banner: {banner}")

                        with open("scan_results.txt", "a") as f:
                            f.write(f"      Banner: {banner}\n")
            else:
                print(Fore.RED + "   No common ports open")

            print()