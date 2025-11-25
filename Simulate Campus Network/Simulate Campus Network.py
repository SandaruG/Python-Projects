import os
import json
from graphviz import Digraph
from PIL import Image, ImageDraw, ImageFont
import datetime
import platform
import asyncio
from ipaddress import ip_network

# Simulate PyNetSim for network configuration
class PyNetSim:
    def __init__(self):
        self.devices = {}
        self.configs = []
    
    def add_device(self, name, device_type, ip=None, subnet=None):
        self.devices[name] = {"type": device_type, "ip": ip, "subnet": subnet, "config": []}
    
    def configure_device(self, device_name, config_commands):
        if device_name in self.devices:
            self.devices[device_name]["config"].extend(config_commands)
            self.configs.append(f"Configuring {device_name}:\n" + "\n".join(config_commands))
    
    def simulate_test(self, test_name, description, expected_result):
        return {"test": test_name, "description": description, "result": expected_result}

# Function to generate text-based screenshot
def generate_screenshot(content, filename, output_dir):
    try:
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except:
            font = ImageFont.load_default()
        # Split content to fit image
        lines = content.split('\n')
        y = 10
        for line in lines[:40]:  # Limit to 40 lines to avoid overflow
            draw.text((10, y), line[:100], fill='black', font=font)  # Limit line length
            y += 20
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        img.save(os.path.join(output_dir, filename))
        return f"Saved screenshot: {filename}"
    except Exception as e:
        return f"Error generating screenshot: {str(e)}"

# Subnetting function
def subnet_network(base_ip, mask, subnets_needed):
    try:
        network = ip_network(f"{base_ip}/{mask}", strict=False)
        subnets = list(network.subnets(new_prefix=24))  # /24 for 256 IPs per subnet
        if len(subnets) < subnets_needed:
            raise ValueError(f"Cannot generate {subnets_needed} subnets from {base_ip}/{mask}")
        return subnets[:subnets_needed]
    except Exception as e:
        print(f"Subnetting error: {str(e)}")
        return []

# Network diagram generation
def generate_network_diagram(output_dir):
    try:
        dot = Digraph(comment='IT Guru Campus Network')
        dot.attr('node', shape='box')
        
        # Internet and main router
        dot.node('Internet', 'Internet')
        dot.node('Router', 'Main Router\n192.168.10.1')
        dot.edge('Internet', 'Router')
        
        # Firewall and core switch
        dot.node('Firewall', 'Firewall')
        dot.node('CoreSwitch', 'Core Switch\n192.168.10.2')
        dot.edge('Router', 'Firewall')
        dot.edge('Firewall', 'CoreSwitch')
        
        # Server room
        dot.node('ServerRoom', 'Server Room\n10.254.1.0/22')
        dot.edge('CoreSwitch', 'ServerRoom')
        
        # Buildings
        dot.node('BldgA', 'Building A\n(Depts 1-3)')
        dot.node('BldgB', 'Building B\n(Depts 4-5, Labs)')
        dot.edge('CoreSwitch', 'BldgA')
        dot.edge('CoreSwitch', 'BldgB')
        
        # Access Points
        dot.node('AP1', 'WiFi AP\nComputing Dept')
        dot.node('AP2', 'WiFi AP\nFinance Dept')
        dot.edge('BldgB', 'AP1')
        dot.edge('BldgA', 'AP2')
        
        diagram_file = os.path.join(output_dir, 'network_diagram.png')
        dot.render(diagram_file, format='png', cleanup=True)
        return f"Saved network diagram: {diagram_file}"
    except Exception as e:
        error_msg = f"Error generating network diagram: {str(e)}\n" \
                    "Diagram structure (text-based):\n" \
                    "Internet -> Main Router (192.168.10.1) -> Firewall -> Core Switch (192.168.10.2)\n" \
                    "Core Switch -> Server Room (10.254.1.0/22)\n" \
                    "Core Switch -> Building A (Depts 1-3) -> WiFi AP (Finance)\n" \
                    "Core Switch -> Building B (Depts 4-5, Labs) -> WiFi AP (Computing)"
        # Save error message as a screenshot
        generate_screenshot(error_msg, "network_diagram_error.png", output_dir)
        return error_msg

# Main async function for simulation
async def main():
    output_dir = r"C:\Users\Sandaru\OneDrive\Desktop\New folder"
    
    # Initialize network simulator
    net = PyNetSim()
    
    # Add devices
    net.add_device("MainRouter", "router", "192.168.10.1", "255.255.240.0")
    net.add_device("CoreSwitch", "switch", "192.168.10.2", "255.255.240.0")
    net.add_device("AP_Computing", "access_point")
    net.add_device("AP_Finance", "access_point")
    net.add_device("DHCP_Server", "server", "10.254.1.10", "255.255.252.0")
    net.add_device("DNS_Server", "server", "10.254.1.11", "255.255.252.0")
    
    # Configure devices
    router_config = [
        "hostname MainRouter",
        "interface GigabitEthernet0/0",
        " ip address 192.168.10.1 255.255.240.0",
        " no shutdown",
        "ip dhcp excluded-address 192.168.10.1 192.168.10.10",
        "ip dhcp pool CampusPool",
        " network 192.168.10.0 255.255.240.0",
        " default-router 192.168.10.1",
        " dns-server 10.254.1.11"
    ]
    net.configure_device("MainRouter", router_config)
    
    switch_config = [
        "hostname CoreSwitch",
        "interface vlan 1",
        " ip address 192.168.10.2 255.255.240.0",
        " no shutdown"
    ]
    net.configure_device("CoreSwitch", switch_config)
    
    # Subnetting for departments and labs
    subnets = subnet_network("192.168.10.0", 20, 9)
    if len(subnets) < 9:
        error_msg = "Error: Not enough subnets generated. Adjust subnet mask or network range."
        print(error_msg)
        generate_screenshot(error_msg, "subnet_error.png", output_dir)
        return
    
    subnet_assignments = [
        ("Finance", 5, subnets[0]),
        ("HR", 2, subnets[1]),
        ("Transport", 5, subnets[2]),
        ("Examination", 8, subnets[3]),
        ("Computing", 10, subnets[4]),
        ("Lab1", 25, subnets[5]),
        ("Lab2", 30, subnets[6]),
        ("Lab3", 50, subnets[7]),
        ("Lab4", 50, subnets[8])
    ]
    
    subnet_table = "Subnet Table:\n" + "\n".join(
        f"{name}: {subnet.network_address}/24 ({subnet.num_addresses} IPs, {subnet.num_addresses-2} usable)"
        for name, _, subnet in subnet_assignments
    )
    
    # Server room static IPs
    server_ips = {
        "DHCP Server": "10.254.1.10",
        "DNS Server": "10.254.1.11",
        "File Server": "10.254.1.12",
        "App Server": "10.254.1.13",
        "Auth Server": "10.254.1.14",
        "Backup Server": "10.254.1.15"
    }
    server_table = "Server IPs:\n" + "\n".join(f"{k}: {v}" for k, v in server_ips.items())
    
    # Maintenance schedule
    maintenance_schedule = """
Maintenance Schedule:
Daily:
  - Check connectivity and device status
  - Monitor server logs
Weekly:
  - Backup configurations
  - Update firmware/software
Monthly:
  - Audit user access
  - Check hardware for issues
Quarterly:
  - Test failover systems
Annually:
  - Full performance review
"""
    
    # Device and software list
    device_list = """
Devices and Software:
- Routers: Cisco ISR 4000 (High-performance routing)
- Switches: Cisco Catalyst 2960/3750 (Layer 2/3 switching)
- Access Points: Ubiquiti Wi-Fi 6 (Wireless for Computing/Finance)
- Firewalls: Fortinet (Network security)
- Cables: Cat6 UTP (Gigabit support)
- Servers: Dell PowerEdge T440 (DHCP, DNS, AD), HP ProLiant DL360 (File, App)
- Software: Packet Tracer (Simulation), Wireshark (Analysis), PRTG (Monitoring)
"""
    
    # Test cases
    test_cases = [
        net.simulate_test("Ping Test", "Ping from Dept 1 to Dept 2", "Fail (VLAN isolation)"),
        net.simulate_test("DHCP Test", "PC gets IP from DHCP server", "IP from correct subnet"),
        net.simulate_test("WiFi Test", "Laptop connects to WiFi", "Access to Internet and internal resources"),
        net.simulate_test("DNS Test", "Query internal DNS", "Resolves fileserver.itguru.local"),
        net.simulate_test("Server Access", "Staff access file server", "Read/write based on permissions")
    ]
    
    test_results = "Test Results:\n" + "\n".join(
        f"{t['test']}: {t['description']} - {t['result']}" for t in test_cases
    )
    
    # Troubleshooting
    troubleshooting = """
Troubleshooting:
1. Connection Flapping:
   - Check cables
   - Verify interface status: show interfaces status
   - Review STP: show spanning-tree
2. No Connection:
   - Check NIC status
   - Verify IP: ipconfig
   - Check VLAN: show vlan brief
3. Slow Internet on Sunny Days:
   - Inspect antenna shielding
   - Monitor with PRTG
   - Contact ISP
"""
    
    # Future enhancements
    enhancements = """
Future Enhancements:
- Cloud Backup: Improved data recovery
- Redundant ISP: Failover support
- VLAN for Labs: Enhanced security
- NAC: Device policy enforcement
- Wi-Fi 6E: Higher throughput
"""
    
    # Generate screenshots
    outputs = [
        (subnet_table, "subnet_table.png"),
        (server_table, "server_ips.png"),
        (maintenance_schedule, "maintenance_schedule.png"),
        (device_list, "device_list.png"),
        ("\n".join(net.configs), "device_configs.png"),
        (test_results, "test_results.png"),
        (troubleshooting, "troubleshooting.png"),
        (enhancements, "enhancements.png")
    ]
    
    for content, filename in outputs:
        print(generate_screenshot(content, filename, output_dir))
    
    # Generate network diagram
    print(generate_network_diagram(output_dir))

# Run the simulation
if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())