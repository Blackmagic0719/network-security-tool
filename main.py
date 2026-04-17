import os
from colorama import Fore, Style, init

# Try to import your local scanning logic
try:
    from scanner import scan_network, scan_ports, get_base_ip
except ImportError:
    # Fallback/Mock functions if scanner.py is missing
    def get_base_ip(): return "192.168.1"
    def scan_network(ip): print(f"{Fore.MAGENTA}Divining spirits on {ip}.x...")
    def scan_ports(ip): return [(80, "Apache/2.4.41"), (443, "OpenSSL")]

# Initialize Colorama
init(autoreset=True)

def clear():
    """Clears the terminal for Windows or Linux/Mac."""
    os.system("cls" if os.name == "nt" else "clear")

def display_banner():
    """Renders the arcane ASCII banner and system status."""
    print(Fore.MAGENTA + Style.BRIGHT + r"""
    ██████╗ ██╗      █████╗  ██████╗██╗  ██╗    ███╗   ███╗ █████╗  ██████╗ ██╗ ██████╗
    ██╔══██╗██║     ██╔══██╗██╔════╝██║ ██╔╝    ████╗ ████║██╔══██╗██╔════╝ ██║██╔════╝
    ██████╔╝██║     ███████║██║     █████╔╝     ██╔████╔██║███████║██║  ███╗██║██║     
    ██╔══██╗██║     ██╔══██║██║     ██╔═██╗     ██║╚██╔╝██║██╔══██║██║   ██║██║██║     
    ██████╔╝███████╗██║  ██║╚██████╗██║  ██╗    ██║ ╚═╝ ██║██║  ██║╚██████╔╝██║╚██████╔╝
    ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝    ╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝ ╚═════╝
    """)
    print(Fore.MAGENTA + "          --- ⛧ [SYSTEM] DARK ENGINE v2.0 READY ⛧ ---")
    print(Fore.RED + "\n[STATUS] ARCANE PROTOCOLS ACTIVE")
    print(Fore.GREEN + "Type 'help' to see the grimoire of commands\n")

def help_menu():
    """Displays available commands with mystical descriptions."""
    print(Fore.CYAN + "\nCOMMAND GRIMOIRE:")
    print(f"{Fore.YELLOW}  scan network {Fore.WHITE} -> Discover all devices in your realm")
    print(f"{Fore.YELLOW}  scan <ip>    {Fore.WHITE} -> Peer into the open gates of a specific target")
    print(f"{Fore.YELLOW}  clear        {Fore.WHITE} -> Purge the ritual chamber (clear screen)")
    print(f"{Fore.YELLOW}  exit         {Fore.WHITE} -> Terminate the session\n")

def main_cli():
    while True:
        # Prompt with the 'analyst' feel from script 1
        cmd = input(Fore.MAGENTA + "analyst " + Fore.RED + "⛧ " + Fore.YELLOW + ">> " + Fore.WHITE).strip().lower()

        if not cmd:
            continue

        if cmd == "help":
            help_menu()

        elif cmd == "clear":
            clear()
            display_banner()

        elif cmd == "exit":
            print(Fore.RED + "[SYSTEM] Banishing session... Goodbye.")
            break

        elif cmd == "scan network":
            base_ip = get_base_ip()
            print(Fore.CYAN + f"\n[ARCANE] Scanning network: {base_ip}.0/24...")
            scan_network(base_ip)
            print(Fore.MAGENTA + "\n" + "-"*40)

        elif cmd.startswith("scan "):
            try:
                target_ip = cmd.split(" ")[1]
                print(Fore.CYAN + f"\n[SYSTEM] Peering into the gates of {target_ip}...")
                
                ports = scan_ports(target_ip)

                print(Fore.GREEN + f"\n[TARGET] {target_ip}")
                if ports:
                    for port, banner in ports:
                        print(Fore.CYAN + f"   Port {port} " + Fore.GREEN + "OPEN")
                        if banner:
                            print(Fore.YELLOW + f"      Banner: {banner}")
                else:
                    print(Fore.RED + "   No common ports open or target is warded.")
            except IndexError:
                print(Fore.RED + "[ERROR] You must specify an IP. Usage: scan 192.168.1.1")
            
            print(Fore.MAGENTA + "\n" + "-"*40)

        else:
            print(Fore.RED + "[SYSTEM] Invalid command. The spirits are confused.")

if __name__ == "__main__":
    clear()
    display_banner()
    main_cli()