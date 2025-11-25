import os
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import numpy as np

# Directories
BASE_OUTPUT_DIR = r"C:\Users\Sandaru\Cisco Packet Tracer 8.2.1\saves"
OUTPUT_SUBDIR = os.path.join(BASE_OUTPUT_DIR, "task_3_2nd")
PACKET_TRACER_DIR = r"C:\Program Files\Cisco Packet Tracer 8.2.1"
ICON_DIR = r"Folder"

# Cisco logo path (optional, place cisco_logo.png in C:\Users\Sandaru)
CISCO_LOGO_PATH = r"C:\Users\Sandaru\cisco_logo.png"

# Font path (optional, place font.ttf in C:\Users\Sandaru)
FONT_PATH = r"C:\Users\Username\font.ttf"

# Device icon paths (update if found in PACKET_TRACER_DIR)
ICON_PATHS = {
    "cloud": os.path.join(ICON_DIR, "pt_cloud.png"),
    "router": os.path.join(ICON_DIR, "router_4331.png"),
    "firewall": os.path.join(ICON_DIR, "router_1941.png"),
    "switch": os.path.join(ICON_DIR, "switch_2950.png"),
    "server": os.path.join(ICON_DIR, "server_pt.png"),
    "ap": os.path.join(ICON_DIR, "pt_accesspoint.png"),
    "building": os.path.join(ICON_DIR, "switch_2950.png")  # Reuse switch for building
}

def generate_topology_diagram():
    try:
        # Create output directory
        os.makedirs(OUTPUT_SUBDIR, exist_ok=True)
        
        # Initialize image
        img = Image.new('RGB', (1200, 900), color='white')
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype(FONT_PATH if os.path.exists(FONT_PATH) else "cour.ttf", 12)
        except:
            font = ImageFont.load_default()

        # Add Cisco logo or text
        if os.path.exists(CISCO_LOGO_PATH):
            logo = Image.open(CISCO_LOGO_PATH).resize((100, 50))
            img.paste(logo, (10, 10), logo.convert('RGBA').split()[3])
        else:
            draw.text((10, 10), "Cisco Systems", fill='black', font=font)
        draw.text((10, 70), "IT Guru Star Topology", fill='blue', font=font)

        # Device definitions (star topology, CoreSwitch at center)
        devices = [
            ("CoreSwitch", (600, 450), "switch", "192.168.10.2/20"),
            ("Cloud", (300, 200), "cloud", "Internet"),
            ("MainRouter", (400, 300), "router", "192.168.10.1/20"),
            ("Firewall", (500, 400), "firewall", "192.168.10.3/20"),
            ("Server Room", (700, 400), "server", "10.254.1.0/22"),
            ("AP_Finance", (600, 300), "ap", "VLAN 10"),
            ("AP_Computing", (600, 600), "ap", "VLAN 14"),
            ("Building A", (500, 500), "building", "VLANs 10-13"),
            ("Building B", (700, 500), "building", "VLANs 15-18")
        ]

        # Load and draw device icons
        for name, (x, y), device_type, label in devices:
            icon_path = ICON_PATHS.get(device_type, ICON_PATHS["switch"])
            if os.path.exists(icon_path):
                icon = Image.open(icon_path).resize((64, 64))
                img.paste(icon, (int(x-32), int(y-32)), icon.convert('RGBA').split()[3])
            else:
                # Fallback: Draw simple shape if icon not found
                if device_type == "cloud":
                    theta = np.linspace(0, 2*np.pi, 12)
                    radius = 30
                    points = [(x + radius * (1 + 0.2 * np.sin(8 * t)) * np.cos(t),
                               y + radius * (1 + 0.2 * np.sin(8 * t)) * np.sin(t))
                              for t in theta]
                    draw.polygon(points, outline='black', fill='#ADD8E6')
                elif device_type in ["router", "firewall"]:
                    draw.rectangle((x-40, y-20, x+40, y+20), outline='black', fill='#ADD8E6')
                    draw.line((x-40, y, x-50, y), fill='black', width=2)
                    draw.line((x+40, y, x+50, y), fill='black', width=2)
                elif device_type == "switch":
                    draw.rectangle((x-40, y-20, x+40, y+20), outline='black', fill='#90EE90')
                    for i in [-20, -10, 0, 10, 20]:
                        draw.line((x+i, y+20, x+i, y+30), fill='black', width=2)
                elif device_type == "server":
                    draw.rectangle((x-30, y-30, x+30, y+30), outline='black', fill='lightgray')
                    for dy in [-20, 0, 20]:
                        draw.line((x-20, y+dy, x+20, y+dy), fill='black', width=1)
                elif device_type == "building":
                    draw.rectangle((x-40, y-20, x+40, y+20), outline='black', fill='lightyellow')
                    draw.polygon([(x-40, y-20), (x, y-40), (x+40, y-20)], outline='black', fill='lightyellow')
                else:  # AP
                    draw.ellipse((x-20, y-20, x+20, y+20), outline='black', fill='#E0FFFF')
                    draw.line((x, y-20, x, y-30), fill='black', width=2)
                    draw.ellipse((x-15, y-15, x+15, y-15), outline='black', fill=None)
            draw.text((x-30, y+35), name, fill='black', font=font)
            draw.text((x-50, y+55), label, fill='black', font=font)

        # Connections (all to CoreSwitch)
        connections = [
            ((350, 200), (600, 450), "serial"),  # Cloud -> CoreSwitch
            ((450, 300), (600, 450)),  # MainRouter -> CoreSwitch
            ((550, 400), (600, 450)),  # Firewall -> CoreSwitch
            ((650, 400), (600, 450)),  # Server Room -> CoreSwitch
            ((600, 350), (600, 450), "dashed"),  # AP_Finance -> CoreSwitch
            ((600, 550), (600, 450), "dashed"),  # AP_Computing -> CoreSwitch
            ((550, 500), (600, 450)),  # Building A -> CoreSwitch
            ((650, 500), (600, 450))   # Building B -> CoreSwitch
        ]

        for (x1, y1), (x2, y2), *line_style in connections:
            if line_style and line_style[0] == "serial":
                draw.line((x1, y1, x2, y2), fill='red', width=3)
            elif line_style and line_style[0] == "dashed":
                dash = 5
                dx, dy = x2 - x1, y2 - y1
                length = (dx**2 + dy**2)**0.5
                if length == 0: continue
                dx, dy = dx/length, dy/length
                pos = 0
                while pos < length:
                    start = (x1 + pos*dx, y1 + pos*dy)
                    end = (x1 + min(pos + dash, length)*dx, y1 + min(pos + dash, length)*dy)
                    draw.line(start + end, fill='black', width=2)
                    pos += dash * 2
            else:
                draw.line((x1, y1, x2, y2), fill='green', width=2)

        # Save image
        img_path = os.path.join(OUTPUT_SUBDIR, "topology.png")
        img.save(img_path)
        return f"Saved topology image: {img_path}"
    except Exception as e:
        return f"Error making topology image: {str(e)}"

# Run the script
if __name__ == "__main__":
    try:
        if not os.path.exists(BASE_OUTPUT_DIR):
            os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)
            print(f"Created base directory: {BASE_OUTPUT_DIR}")
        print("\n=== IT Guru Packet Tracer Star Topology ===")
        print("Drawing topology with real Packet Tracer icons. Check saves folder.")
        print(generate_topology_diagram())
    except Exception as e:
        print(f"Main: Error running script: {str(e)}")
