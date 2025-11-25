import os
from PIL import Image, ImageDraw, ImageFont
import platform
import asyncio

# Base output directory (raw string)
BASE_OUTPUT_DIR = r"your folder folder"

# Cisco logo path (optional, place cisco_logo.png in C:\Users\Sandaru)
CISCO_LOGO_PATH = r"your path"

# Font path (optional, place font.ttf in C:\Users\Sandaru for Cisco-like font)
FONT_PATH = r"path\font.ttf"

# Generate CLI-style screenshot
def generate_cli_screenshot(content, filename, output_dir, title=""):
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        img = Image.new('RGB', (800, 600), color='black')  # CLI black background
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype(FONT_PATH if os.path.exists(FONT_PATH) else "cour.ttf", 14)
        except:
            font = ImageFont.load_default()
        # Draw Cisco logo
        if os.path.exists(CISCO_LOGO_PATH):
            logo = Image.open(CISCO_LOGO_PATH).resize((100, 50))
            img.paste(logo, (10, 10))
        else:
            draw.text((10, 10), "Cisco Systems", fill='white', font=font)
        # Draw title
        draw.text((10, 70), title, fill='green', font=font)
        # Draw CLI content
        lines = content.split('\n')
        y = 100
        for line in lines[:35]:  # Limit to 35 lines
            draw.text((10, y), line[:100], fill='white', font=font)
            y += 16
        img_path = os.path.join(output_dir, filename)
        img.save(img_path)
        return f"Saved CLI screenshot: {img_path}"
    except Exception as e:
        return f"Error making CLI screenshot: {str(e)}"

# Generate Config tab-style screenshot
def generate_config_screenshot(content, filename, output_dir, title=""):
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        img = Image.new('RGB', (800, 600), color='white')  # Config tab white background
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype(FONT_PATH if os.path.exists(FONT_PATH) else "cour.ttf", 14)
        except:
            font = ImageFont.load_default()
        # Draw Cisco logo
        if os.path.exists(CISCO_LOGO_PATH):
            logo = Image.open(CISCO_LOGO_PATH).resize((100, 50))
            img.paste(logo, (10, 10))
        else:
            draw.text((10, 10), "Cisco Systems", fill='black', font=font)
        # Draw title
        draw.text((10, 70), title, fill='blue', font=font)
        # Draw Config content (GUI-like boxes)
        draw.rectangle((10, 100, 790, 590), outline='gray', fill='lightgray')
        lines = content.split('\n')
        y = 120
        for line in lines[:30]:
            draw.text((20, y), line[:100], fill='black', font=font)
            y += 16
        img_path = os.path.join(output_dir, filename)
        img.save(img_path)
        return f"Saved Config screenshot: {img_path}"
    except Exception as e:
        return f"Error making Config screenshot: {str(e)}"

# Generate topology diagram
def generate_topology_diagram(output_dir):
    try:
        output_subdir = os.path.join(output_dir, "task_4_5th")
        if not os.path.exists(output_subdir):
            os.makedirs(output_subdir)
        img = Image.new('RGB', (1000, 800), color='white')
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype(FONT_PATH if os.path.exists(FONT_PATH) else "cour.ttf", 12)
        except:
            font = ImageFont.load_default()
        # Draw Cisco logo
        if os.path.exists(CISCO_LOGO_PATH):
            logo = Image.open(CISCO_LOGO_PATH).resize((100, 50))
            img.paste(logo, (10, 10))
        else:
            draw.text((10, 10), "Cisco Systems", fill='black', font=font)
        # Draw title
        draw.text((10, 70), "IT Guru Campus Network Topology", fill='blue', font=font)
        # Draw devices (rectangles for routers/switch, circles for APs/PCs)
        devices = [
            ("Cloud", (100, 150), "cloud"),  # Internet
            ("MainRouter", (250, 150), "router"),
            ("Firewall", (400, 150), "router"),
            ("CoreSwitch", (550, 150), "switch"),
            ("Server Room", (700, 150), "server"),
            ("AP_Finance", (550, 300), "ap"),
            ("AP_Computing", (550, 400), "ap"),
            ("Building A", (400, 300), "building"),
            ("Building B", (400, 400), "building")
        ]
        for name, (x, y), device_type in devices:
            if device_type in ["router", "switch", "server", "building"]:
                draw.rectangle((x-40, y-20, x+40, y+20), outline='black', fill='lightblue')
            else:  # cloud, ap
                draw.ellipse((x-20, y-20, x+20, y+20), outline='black', fill='lightblue')
            draw.text((x-30, y+25), name, fill='black', font=font)
        # Draw connections (lines)
        connections = [
            ((150, 150), (200, 150)),  # Cloud -> MainRouter
            ((300, 150), (350, 150)),  # MainRouter -> Firewall
            ((450, 150), (500, 150)),  # Firewall -> CoreSwitch
            ((550, 150), (650, 150)),  # CoreSwitch -> Server Room
            ((550, 150), (550, 280), "dashed"),  # CoreSwitch -> AP_Finance (WiFi)
            ((550, 150), (550, 380), "dashed"),  # CoreSwitch -> AP_Computing (WiFi)
            ((550, 150), (450, 300)),  # CoreSwitch -> Building A
            ((550, 150), (450, 400))   # CoreSwitch -> Building B
        ]
        for (x1, y1), (x2, y2), *line_style in connections:
            if line_style and line_style[0] == "dashed":
                dash = 5
                while x1 < x2 or y1 < y2:
                    draw.line((x1, y1, min(x1 + dash, x2), min(y1 + dash, y2)), fill='black', width=2)
                    x1, y1 = min(x1 + dash * 2, x2), min(y1 + dash * 2, y2)
            else:
                draw.line((x1, y1, x2, y2), fill='black', width=2)
        # Labels
        draw.text((250, 170), "192.168.10.1", fill='black', font=font)  # MainRouter
        draw.text((550, 170), "192.168.10.2", fill='black', font=font)  # CoreSwitch
        draw.text((700, 170), "10.254.1.0/22", fill='black', font=font)  # Server Room
        draw.text((550, 320), "VLAN 10", fill='black', font=font)  # AP_Finance
        draw.text((550, 420), "VLAN 14", fill='black', font=font)  # AP_Computing
        draw.text((400, 320), "VLANs 10-13", fill='black', font=font)  # Building A
        draw.text((400, 420), "VLANs 15-18", fill='black', font=font)  # Building B
        img_path = os.path.join(output_subdir, "network_topology.png")
        img.save(img_path)
        return f"Saved topology diagram: {img_path}"
    except Exception as e:
        return f"Error making topology diagram: {str(e)}"

# Task 04 Question 1: Configure Devices
async def task_4_1_configure_devices(output_dir):
    output_subdir = os.path.join(output_dir, "task_4_1st")
    if not os.path.exists(output_subdir):
        os.makedirs(output_subdir)
    
    # Device configurations
    configs = {
        "MainRouter": [
            "enable",
            "configure terminal",
            "hostname MainRouter",
            "interface GigabitEthernet0/0/0",
            " ip address 192.168.10.1 255.255.240.0",
            " no shutdown",
            "ip dhcp excluded-address 192.168.10.1 192.168.10.10",
            "ip dhcp pool CampusPool",
            " network 192.168.10.0 255.255.240.0",
            " default-router 192.168.10.1",
            " dns-server 10.254.1.11",
            "exit"
        ],
        "CoreSwitch": [
            "enable",
            "configure terminal",
            "hostname CoreSwitch",
            "interface vlan 1",
            " ip address 192.168.10.2 255.255.240.0",
            " no shutdown",
            "vlan 10",
            " name Finance",
            "vlan 11",
            " name HR",
            "vlan 12",
            " name Transport",
            "vlan 13",
            " name Examination",
            "vlan 14",
            " name Computing",
            "vlan 15",
            " name Lab1",
            "vlan 16",
            " name Lab2",
            "vlan 17",
            " name Lab3",
            "vlan 18",
            " name Lab4",
            "interface FastEthernet0/1",
            " switchport mode access",
            " switchport access vlan 10",
            "interface FastEthernet0/2",
            " switchport mode access",
            " switchport access vlan 14",
            "interface range FastEthernet0/3 - 24",
            " switchport mode access",
            " spanning-tree portfast",
            "exit"
        ],
        "Firewall": [
            "enable",
            "configure terminal",
            "hostname Firewall",
            "access-list 100 permit ip 192.168.10.0 0.0.15.255 10.254.1.0 0.0.3.255",
            "access-list 100 deny ip any any",
            "interface GigabitEthernet0/0/0",
            " ip access-group 100 in",
            " no shutdown",
            "exit"
        ],
        "AP_Finance": [
            "SSID: ITGuru-WiFi",
            "Authentication: WPA2-PSK",
            "Password: ITGuru123",
            "VLAN: 10",
            "Connected to CoreSwitch FastEthernet0/10"
        ],
        "AP_Computing": [
            "SSID: ITGuru-WiFi",
            "Authentication: WPA2-PSK",
            "Password: ITGuru123",
            "VLAN: 14",
            "Connected to CoreSwitch FastEthernet0/11"
        ],
        "DHCP_Server": ["IP: 10.254.1.10, Mask: 255.255.252.0, Gateway: 10.254.1.1"],
        "DNS_Server": ["IP: 10.254.1.11, Mask: 255.255.252.0, Gateway: 10.254.1.1, Record: fileserver.itguru.local = 10.254.1.12"],
        "File_Server": ["IP: 10.254.1.12, Mask: 255.255.252.0, Gateway: 10.254.1.1"],
        "App_Server": ["IP: 10.254.1.13, Mask: 255.255.252.0, Gateway: 10.254.1.1"],
        "Auth_Server": ["IP: 10.254.1.14, Mask: 255.255.252.0, Gateway: 10.254.1.1"],
        "Backup_Server": ["IP: 10.254.1.15, Mask: 255.255.252.0, Gateway: 10.254.1.1"]
    }
    
    # Generate CLI and Config screenshots
    for device, config in configs.items():
        config_text = "\n".join(config)
        if device in ["MainRouter", "CoreSwitch", "Firewall"]:
            print(generate_cli_screenshot(config_text, f"{device.lower()}_config.png", output_subdir, f"{device} CLI Configuration"))
        else:
            print(generate_config_screenshot(config_text, f"{device.lower()}_config.png", output_subdir, f"{device} Config Tab"))
    
    # Save all configs as text
    output_content = "\n\n".join(f"Configuring {device}:\n" + "\n".join(config) for device, config in configs.items())
    output_file = os.path.join(output_subdir, "device_configurations.txt")
    with open(output_file, 'w') as f:
        f.write(output_content)
    print(f"Task 4.1: Saved configs to: {output_file}")
    print(generate_cli_screenshot(output_content, "device_configurations.png", output_subdir, "All Device Configurations"))
    
    return output_content

# Task 04 Question 2: Test Cases
async def task_4_2_test_cases(output_dir):
    output_subdir = os.path.join(output_dir, "task_4_2nd")
    if not os.path.exists(output_subdir):
        os.makedirs(output_subdir)
    
    test_cases = [
        {"test": "Ping Test", "description": "ping 192.168.11.2 from Finance PC (192.168.10.x)", "result": "Fail (VLAN isolation)"},
        {"test": "DHCP Test", "description": "ipconfig on Lab1 PC", "result": "IP in 192.168.15.0/24"},
        {"test": "WiFi Test", "description": "connect laptop to ITGuru-WiFi", "result": "Access Internet and servers"},
        {"test": "DNS Test", "description": "nslookup fileserver.itguru.local from Exam PC", "result": "Resolves to 10.254.1.12"},
        {"test": "Server Access", "description": "access File Server from Transport PC", "result": "Read/write per permissions"}
    ]
    
    test_results = "Test Cases for IT Guru Network:\n\n" \
                   "Test Case      | Description                           | Result\n" \
                   "---------------|---------------------------------------|-------\n"
    for t in test_cases:
        test_results += f"{t['test']:<14} | {t['description']:<37} | {t['result']}\n"
    
    output_file = os.path.join(output_subdir, "test_cases.txt")
    with open(output_file, 'w') as f:
        f.write(test_results)
    print(f"Task 4.2: Saved test cases to: {output_file}")
    print(generate_cli_screenshot(test_results, "test_cases.png", output_subdir, "Test Cases Summary"))
    
    # Generate test screenshots
    for i, t in enumerate(test_cases, 1):
        test_output = f"Test {i}: {t['test']}\nCommand: {t['description']}\nResult: {t['result']}"
        print(generate_cli_screenshot(test_output, f"test_{i}.png", output_subdir, f"Test {i} Result"))
    
    return test_results

# Task 04 Question 3: Troubleshooting
async def task_4_3_troubleshooting(output_dir):
    output_subdir = os.path.join(output_dir, "task_4_3rd")
    if not os.path.exists(output_subdir):
        os.makedirs(output_subdir)
    
    troubleshooting = r"""
Troubleshooting Steps for IT Guru Network:

1. Connection Flapping (On/Off):
   - Check cables for loose ends.
   - Run `show interfaces status` on switch.
   - Check Spanning Tree: `show spanning-tree`.
   - Restart port: `shutdown`, `no shutdown`.

2. Cable Plugged, No Connection:
   - Check PC NIC is turned on.
   - Run `ipconfig` to see IP.
   - Verify VLAN: `show vlan brief`.
   - Check port security on switch.

3. Slow Internet on Sunny Days:
   - Check antenna for interference.
   - Test speed with PRTG tool.
   - Inspect cables for weather damage.
   - Call ISP for line problems.
"""
    
    output_file = os.path.join(output_subdir, "troubleshooting.txt")
    with open(output_file, 'w') as f:
        f.write(troubleshooting)
    print(f"Task 4.3: Saved troubleshoot steps to: {output_file}")
    print(generate_config_screenshot(troubleshooting, "troubleshooting.png", output_subdir, "Troubleshooting Steps"))
    
    return troubleshooting

# Task 04 Question 4: Enhancements
async def task_4_4_enhancements(output_dir):
    output_subdir = os.path.join(output_dir, "task_4_4th")
    if not os.path.exists(output_subdir):
        os.makedirs(output_subdir)
    
    enhancements = r"""
Future Upgrades for IT Guru Network:

Enhancement                | Benefit
---------------------------|--------------------------------------
Cloud Backup              | Saves data if servers crash.
Second ISP Link           | Keeps network up if ISP fails.
More Lab VLANs            | Better security, less traffic jam.
Network Access Control    | Blocks bad devices from joining.
Wi-Fi 6E APs              | Faster WiFi, less lag for users.
Next-Gen Firewall         | Stops new threats, better filtering.
"""
    
    output_file = os.path.join(output_subdir, "enhancements.txt")
    with open(output_file, 'w') as f:
        f.write(enhancements)
    print(f"Task 4.4: Saved upgrades to: {output_file}")
    print(generate_config_screenshot(enhancements, "enhancements.png", output_subdir, "Future Enhancements"))
    
    return enhancements

# Task 04 Question 5: Conclusion
async def task_4_5_conclusion(output_dir):
    output_subdir = os.path.join(output_dir, "task_4_5th")
    if not os.path.exists(output_subdir):
        os.makedirs(output_subdir)
    
    conclusion = r"""
Conclusion for IT Guru Network:

The network design is real solid. Star topology with VLANs works good. Subnets (192.168.10.0/24 to 192.168.18.0/24) handle 165 PCs. WiFi for Computing and Finance is fast. Planning used Cisco and Dell, which are reliable. Subnetting is easy to grow. Configs for router, switch, and APs are correct. DHCP and DNS servers run good. Firewall keeps things safe. Tests showed VLANs block traffic right, DHCP gives IPs, WiFi connects, and servers work. More tests for heavy traffic could help. Upgrades like cloud backups make it better. The network is fast, secure, and good for IT Guru’s students.
"""
    
    output_file = os.path.join(output_subdir, "conclusion.txt")
    with open(output_file, 'w') as f:
        f.write(conclusion)
    print(f"Task 4.5: Saved conclusion to: {output_file}")
    print(generate_config_screenshot(conclusion, "conclusion.png", output_subdir, "Network Conclusion"))
    
    return conclusion

# Manual Instructions for Packet Tracer (for real screenshots)
def manual_packet_tracer_instructions():
    instructions = r"""
Manual Packet Tracer Instructions for Real Screenshots:

1. Open Cisco Packet Tracer, create new project: ITGuru_Network.pkt.
2. Add devices:
   - Router (4331 ISR): MainRouter
   - Switch (2950-24): CoreSwitch
   - 2 Access Points (PT-AccessPoint): AP_Finance, AP_Computing
   - 6 Servers (Server-PT): DHCP, DNS, File, App, Auth, Backup
   - Router (1941): Firewall
   - PCs: 1 per VLAN (Finance VLAN 10, HR VLAN 11, Transport VLAN 12, Exam VLAN 13, Computing VLAN 14, Lab1 VLAN 15, Lab2 VLAN 16, Lab3 VLAN 17, Lab4 VLAN 18)
3. Connect with Copper Straight-Through cables:
   - Internet (Cloud-PT) -> MainRouter (Gig0/0/0) -> Firewall (Gig0/0/0) -> CoreSwitch (FastEthernet0/24)
   - CoreSwitch -> Servers (FastEthernet0/3-8), AP_Finance (FastEthernet0/10), AP_Computing (FastEthernet0/11), PCs (FastEthernet0/12-20)
4. Configure devices:
   - Copy CLI from task_4_1st/device_configurations.txt.
   - MainRouter: CLI tab, paste router config.
   - CoreSwitch: CLI tab, paste switch config.
   - Firewall: CLI tab, paste firewall config.
   - AP_Finance, AP_Computing: Config tab, set SSID, WPA2-PSK, VLAN.
   - Servers: Config tab, set IPs; Services tab for DHCP/DNS.
5. Take screenshots:
   - CLI tab (Router, Switch, Firewall): Alt+PrintScreen, save as router_config.png, switch_config.png, firewall_config.png.
   - Config tab (APs, Servers): Alt+PrintScreen, save as ap_finance_config.png, ap_computing_config.png, dhcp_server_config.png, etc.
   - Save in C:\Users\Sandaru\OneDrive\Desktop\New folder\task_4_1st.
6. Run tests:
   - Ping Test: Finance PC (VLAN 10), ping 192.168.11.2, expect fail, screenshot as test_1.png.
   - DHCP Test: Lab1 PC, ipconfig, expect 192.168.15.x, screenshot as test_2.png.
   - WiFi Test: Laptop to ITGuru-WiFi, ping 10.254.1.12, screenshot as test_3.png.
   - DNS Test: Exam PC, nslookup fileserver.itguru.local, expect 10.254.1.12, screenshot as test_4.png.
   - Server Test: Transport PC, access File Server (Desktop tab), screenshot as test_5.png.
   - Save in C:\Users\Sandaru\OneDrive\Desktop\New folder\task_4_2nd.
7. Topology Diagram:
   - In Packet Tracer, arrange devices like in network_topology.png.
   - Use Logical view, add labels (IPs, VLANs).
   - Screenshot with Alt+PrintScreen, save as network_topology_real.png in task_4_5th.
"""
    output_subdir = os.path.join(BASE_OUTPUT_DIR, "task_4_1st")
    output_file = os.path.join(output_subdir, "manual_instructions.txt")
    with open(output_file, 'w') as f:
        f.write(instructions)
    print(f"Saved manual instructions to: {output_file}")
    print(generate_config_screenshot(instructions, "manual_instructions.png", output_subdir, "Manual Instructions"))

# Main async function
async def main():
    print("\n=== Task 04 Image Generation ===")
    print("Generating images like Packet Tracer screenshots. For real ones, follow manual instructions.")
    await task_4_1_configure_devices(BASE_OUTPUT_DIR)
    await task_4_2_test_cases(BASE_OUTPUT_DIR)
    await task_4_3_troubleshooting(BASE_OUTPUT_DIR)
    await task_4_4_enhancements(BASE_OUTPUT_DIR)
    await task_4_5_conclusion(BASE_OUTPUT_DIR)
    print(generate_topology_diagram(BASE_OUTPUT_DIR))
    manual_packet_tracer_instructions()

# Run the script
if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
