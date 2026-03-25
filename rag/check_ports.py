import socket
import sys

def is_port_available(port):
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def find_available_port(start_port=8001, max_attempts=10):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(port):
            return port
    return None

def main():
    print("=== Port Checker ===")
    
    # Check common ports
    ports_to_check = [8001, 8002, 8003, 8004, 8005]
    
    print("Checking ports:")
    available_ports = []
    
    for port in ports_to_check:
        if is_port_available(port):
            print(f"✅ Port {port}: Available")
            available_ports.append(port)
        else:
            print(f"❌ Port {port}: In use")
    
    if available_ports:
        print(f"\nRecommended port: {available_ports[0]}")
    else:
        print("\n⚠️ All common ports are in use")
        alt_port = find_available_port(8010)
        if alt_port:
            print(f"Alternative port found: {alt_port}")

if __name__ == "__main__":
    main()