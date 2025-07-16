#!/usr/bin/python3

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info, error
from mininet.cli import CLI
import time
import json
import os
import subprocess
import argparse
import random
import shutil
from datetime import datetime


class LinuxRouter(Node):
    """A node with IP forwarding enabled."""

    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()


class NetworkTopo(Topo):
    
    def build(self, **_opts):
        # Create routers r1 to r18
        routers = {}
        for i in range(1, 19):
            routers[f'r{i}'] = self.addHost(f'r{i}', cls=LinuxRouter)

        # Create hosts
        hosts = {
            'h11': ('10.0.11.100/24', '10.0.11.10'),
            'h12': ('10.0.12.100/24', '10.0.12.10'),
            'h22': ('10.0.22.100/24', '10.0.22.10'),
            'h23': ('10.0.23.100/24', '10.0.23.10'),	
            'h33': ('10.0.33.100/24', '10.0.33.10'),
            'h34': ('10.0.34.100/24', '10.0.34.10'),
            'h13': ('10.0.13.100/24', '10.0.13.10'),
            'h14': ('10.0.14.100/24', '10.0.14.10'),
            'h24': ('10.0.24.100/24', '10.0.24.10'),
            'h25': ('10.0.25.100/24', '10.0.25.10'),
            'h35': ('10.0.35.100/24', '10.0.35.10'),
            'h36': ('10.0.36.100/24', '10.0.36.10'),
        }

        for hname, (hip, hgw) in hosts.items():
            self.addHost(hname, ip=hip, defaultRoute=f'via {hgw}')

        # Host-router links
        self.host_router_links = [
            ('h11', 'r1', 'r1-eth0', '10.0.11.10/24'),
            ('h12', 'r2', 'r2-eth0', '10.0.12.10/24'),
            ('h22', 'r7', 'r7-eth0', '10.0.22.10/24'),
            ('h23', 'r8', 'r8-eth0', '10.0.23.10/24'),
            ('h33', 'r13', 'r13-eth0', '10.0.33.10/24'),
            ('h34', 'r14', 'r14-eth0', '10.0.34.10/24'),
            ('h13', 'r5', 'r5-eth0', '10.0.13.10/24'),
            ('h14', 'r6', 'r6-eth0', '10.0.14.10/24'),
            ('h24', 'r11', 'r11-eth0', '10.0.24.10/24'),
            ('h25', 'r12', 'r12-eth0', '10.0.25.10/24'),
            ('h35', 'r17', 'r17-eth0', '10.0.35.10/24'),
            ('h36', 'r18', 'r18-eth0', '10.0.36.10/24'),
        ]

        # Connect hosts to routers
        for hname, rname, intfName, ip in self.host_router_links:
            self.addLink(hname, routers[rname], intfName2=intfName)

        # Router-router links with explicit interfaces
        self.router_links = [
            ('r1', 'r2', 'r1-eth1', 'r2-eth1', '10.0.1.1/30', '10.0.1.2/30'),
            ('r1', 'r3', 'r1-eth2', 'r3-eth1', '10.0.1.5/30', '10.0.1.6/30'),
            ('r2', 'r4', 'r2-eth2', 'r4-eth1', '10.0.1.9/30', '10.0.1.10/30'),
            ('r3', 'r4', 'r3-eth2', 'r4-eth2', '10.0.1.13/30', '10.0.1.14/30'),
            ('r3', 'r5', 'r3-eth3', 'r5-eth1', '10.0.1.17/30', '10.0.1.18/30'),
            ('r4', 'r6', 'r4-eth3', 'r6-eth1', '10.0.1.21/30', '10.0.1.22/30'),
            ('r5', 'r6', 'r5-eth2', 'r6-eth2', '10.0.1.25/30', '10.0.1.26/30'),
            ('r4', 'r9', 'r4-eth4', 'r9-eth1', '10.0.4.5/30', '10.0.4.6/30'),
            ('r4', 'r10', 'r4-eth5', 'r10-eth1', '10.0.6.5/30', '10.0.6.6/30'),
            ('r4', 'r16', 'r4-eth6', 'r16-eth1', '10.0.5.5/30', '10.0.5.6/30'),
            ('r7', 'r8', 'r7-eth1', 'r8-eth1', '10.0.2.1/30', '10.0.2.2/30'),
            ('r7', 'r9', 'r7-eth2', 'r9-eth2', '10.0.2.5/30', '10.0.2.6/30'),
            ('r8', 'r10', 'r8-eth2', 'r10-eth2', '10.0.2.9/30', '10.0.2.10/30'),
            ('r9', 'r10', 'r9-eth3', 'r10-eth3', '10.0.2.13/30', '10.0.2.14/30'),
            ('r9', 'r11', 'r9-eth4', 'r11-eth1', '10.0.2.17/30', '10.0.2.18/30'),
            ('r10', 'r15', 'r10-eth4', 'r15-eth1', '10.0.7.5/30', '10.0.7.6/30'),
            ('r10', 'r16', 'r10-eth5', 'r16-eth2', '10.0.8.5/30', '10.0.8.6/30'),
            ('r10', 'r12', 'r10-eth6', 'r12-eth1', '10.0.2.21/30', '10.0.2.22/30'),
            ('r11', 'r12', 'r11-eth2', 'r12-eth2', '10.0.2.25/30', '10.0.2.26/30'),
            ('r13', 'r14', 'r13-eth1', 'r14-eth1', '10.0.3.1/30', '10.0.3.2/30'),
            ('r13', 'r15', 'r13-eth2', 'r15-eth2', '10.0.3.5/30', '10.0.3.6/30'),
            ('r14', 'r16', 'r14-eth2', 'r16-eth3', '10.0.3.9/30', '10.0.3.10/30'),
            ('r15', 'r16', 'r15-eth3', 'r16-eth4', '10.0.3.13/30', '10.0.3.14/30'),
            ('r15', 'r17', 'r15-eth4', 'r17-eth1', '10.0.3.17/30', '10.0.3.18/30'),
            ('r16', 'r18', 'r16-eth5', 'r18-eth1', '10.0.3.21/30', '10.0.3.22/30'),
            ('r17', 'r18', 'r17-eth2', 'r18-eth2', '10.0.3.25/30', '10.0.3.26/30'),
        ]

        # Add router-router links
        for rA, rB, intfA, intfB, ipA, ipB in self.router_links:
            self.addLink(routers[rA], routers[rB], intfName1=intfA, intfName2=intfB)


def create_ospf_baseline_config(config_dir):
    """
    Create OSPF baseline configurations with cost 1 for all interfaces
    """
    
    # Complete link definitions
    router_links = [
        ('r1', 'r2', 'r1-eth1', 'r2-eth1', '10.0.1.1/30', '10.0.1.2/30'),
        ('r1', 'r3', 'r1-eth2', 'r3-eth1', '10.0.1.5/30', '10.0.1.6/30'),
        ('r2', 'r4', 'r2-eth2', 'r4-eth1', '10.0.1.9/30', '10.0.1.10/30'),
        ('r3', 'r4', 'r3-eth2', 'r4-eth2', '10.0.1.13/30', '10.0.1.14/30'),
        ('r3', 'r5', 'r3-eth3', 'r5-eth1', '10.0.1.17/30', '10.0.1.18/30'),
        ('r4', 'r6', 'r4-eth3', 'r6-eth1', '10.0.1.21/30', '10.0.1.22/30'),
        ('r5', 'r6', 'r5-eth2', 'r6-eth2', '10.0.1.25/30', '10.0.1.26/30'),
        ('r4', 'r9', 'r4-eth4', 'r9-eth1', '10.0.4.5/30', '10.0.4.6/30'),
        ('r4', 'r10', 'r4-eth5', 'r10-eth1', '10.0.6.5/30', '10.0.6.6/30'),
        ('r4', 'r16', 'r4-eth6', 'r16-eth1', '10.0.5.5/30', '10.0.5.6/30'),
        ('r7', 'r8', 'r7-eth1', 'r8-eth1', '10.0.2.1/30', '10.0.2.2/30'),
        ('r7', 'r9', 'r7-eth2', 'r9-eth2', '10.0.2.5/30', '10.0.2.6/30'),
        ('r8', 'r10', 'r8-eth2', 'r10-eth2', '10.0.2.9/30', '10.0.2.10/30'),
        ('r9', 'r10', 'r9-eth3', 'r10-eth3', '10.0.2.13/30', '10.0.2.14/30'),
        ('r9', 'r11', 'r9-eth4', 'r11-eth1', '10.0.2.17/30', '10.0.2.18/30'),
        ('r10', 'r15', 'r10-eth4', 'r15-eth1', '10.0.7.5/30', '10.0.7.6/30'),
        ('r10', 'r16', 'r10-eth5', 'r16-eth2', '10.0.8.5/30', '10.0.8.6/30'),
        ('r10', 'r12', 'r10-eth6', 'r12-eth1', '10.0.2.21/30', '10.0.2.22/30'),
        ('r11', 'r12', 'r11-eth2', 'r12-eth2', '10.0.2.25/30', '10.0.2.26/30'),
        ('r13', 'r14', 'r13-eth1', 'r14-eth1', '10.0.3.1/30', '10.0.3.2/30'),
        ('r13', 'r15', 'r13-eth2', 'r15-eth2', '10.0.3.5/30', '10.0.3.6/30'),
        ('r14', 'r16', 'r14-eth2', 'r16-eth3', '10.0.3.9/30', '10.0.3.10/30'),
        ('r15', 'r16', 'r15-eth3', 'r16-eth4', '10.0.3.13/30', '10.0.3.14/30'),
        ('r15', 'r17', 'r15-eth4', 'r17-eth1', '10.0.3.17/30', '10.0.3.18/30'),
        ('r16', 'r18', 'r16-eth5', 'r18-eth1', '10.0.3.21/30', '10.0.3.22/30'),
        ('r17', 'r18', 'r17-eth2', 'r18-eth2', '10.0.3.25/30', '10.0.3.26/30'),
    ]

    host_router_links = [
        ('h11', 'r1', 'r1-eth0', '10.0.11.10/24'),
        ('h12', 'r2', 'r2-eth0', '10.0.12.10/24'),
        ('h22', 'r7', 'r7-eth0', '10.0.22.10/24'),
        ('h23', 'r8', 'r8-eth0', '10.0.23.10/24'),
        ('h33', 'r13', 'r13-eth0', '10.0.33.10/24'),
        ('h34', 'r14', 'r14-eth0', '10.0.34.10/24'),
        ('h13', 'r5', 'r5-eth0', '10.0.13.10/24'),
        ('h14', 'r6', 'r6-eth0', '10.0.14.10/24'),
        ('h24', 'r11', 'r11-eth0', '10.0.24.10/24'),
        ('h25', 'r12', 'r12-eth0', '10.0.25.10/24'),
        ('h35', 'r17', 'r17-eth0', '10.0.35.10/24'),
        ('h36', 'r18', 'r18-eth0', '10.0.36.10/24'),
    ]

    # Create interface mapping for routers
    router_interfaces = {}
    for i in range(1, 19):
        router_interfaces[f'r{i}'] = []

    # Add host-router interfaces
    for hname, rname, intfName, ip in host_router_links:
        router_interfaces[rname].append((intfName, ip.split('/')[0], int(ip.split('/')[1])))

    # Add router-router interfaces
    for rA, rB, intfA, intfB, ipA, ipB in router_links:
        router_interfaces[rA].append((intfA, ipA.split('/')[0], int(ipA.split('/')[1])))
        router_interfaces[rB].append((intfB, ipB.split('/')[0], int(ipB.split('/')[1])))

    # Create configuration directory
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    # Generate configuration file for each router
    for router_name, interfaces in router_interfaces.items():
        router_id = int(router_name[1:])
        router_dir = os.path.join(config_dir, router_name)
        
        if not os.path.exists(router_dir):
            os.makedirs(router_dir)
        
        frr_conf_path = os.path.join(router_dir, "frr.conf")
        
        with open(frr_conf_path, 'w') as f:
            f.write(f"# FRR Configuration for {router_name}\n")
            f.write(f"# Auto-generated - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("frr version 8.1\n")
            f.write("frr defaults traditional\n")
            f.write(f"hostname {router_name}\n")
            f.write("log syslog informational\n")
            f.write("service integrated-vtysh-config\n\n")
            
            # Interface configuration with cost 1
            for intf_name, ip_addr, prefix_len in interfaces:
                f.write(f"interface {intf_name}\n")
                f.write(f" ip address {ip_addr}/{prefix_len}\n")
                f.write(f" ip ospf cost 1\n")
                f.write("!\n")
            
            # OSPF configuration
            f.write("router ospf\n")
            f.write(f" router-id {router_id}.{router_id}.{router_id}.{router_id}\n")
            f.write(" log-adjacency-changes\n")
            
            # Advertise networks
            for intf_name, ip_addr, prefix_len in interfaces:
                ip_parts = [int(part) for part in ip_addr.split('.')]
                
                if prefix_len == 30:
                    network_ip = ip_parts.copy()
                    network_ip[3] = (network_ip[3] // 4) * 4
                elif prefix_len == 24:
                    network_ip = ip_parts.copy()
                    network_ip[3] = 0
                
                network_addr = ".".join(map(str, network_ip))
                f.write(f" network {network_addr}/{prefix_len} area 0\n")
            
            f.write("!\n")
            f.write("line vty\n")
            f.write("!\n")

    return True


def select_links_for_asymmetry(percentage, seed):
    """
    Select links for asymmetry based on percentage and seed
    """
    # Complete list of links (26 total links)
    all_links = [
        ('r1', 'r2', 'r1-eth1', 'r2-eth1'),
        ('r1', 'r3', 'r1-eth2', 'r3-eth1'),
        ('r2', 'r4', 'r2-eth2', 'r4-eth1'),
        ('r3', 'r4', 'r3-eth2', 'r4-eth2'),
        ('r3', 'r5', 'r3-eth3', 'r5-eth1'),
        ('r4', 'r6', 'r4-eth3', 'r6-eth1'),
        ('r5', 'r6', 'r5-eth2', 'r6-eth2'),
        ('r4', 'r9', 'r4-eth4', 'r9-eth1'),
        ('r4', 'r10', 'r4-eth5', 'r10-eth1'),
        ('r4', 'r16', 'r4-eth6', 'r16-eth1'),
        ('r7', 'r8', 'r7-eth1', 'r8-eth1'),
        ('r7', 'r9', 'r7-eth2', 'r9-eth2'),
        ('r8', 'r10', 'r8-eth2', 'r10-eth2'),
        ('r9', 'r10', 'r9-eth3', 'r10-eth3'),
        ('r9', 'r11', 'r9-eth4', 'r11-eth1'),
        ('r10', 'r15', 'r10-eth4', 'r15-eth1'),
        ('r10', 'r16', 'r10-eth5', 'r16-eth2'),
        ('r10', 'r12', 'r10-eth6', 'r12-eth1'),
        ('r11', 'r12', 'r11-eth2', 'r12-eth2'),
        ('r13', 'r14', 'r13-eth1', 'r14-eth1'),
        ('r13', 'r15', 'r13-eth2', 'r15-eth2'),
        ('r14', 'r16', 'r14-eth2', 'r16-eth3'),
        ('r15', 'r16', 'r15-eth3', 'r16-eth4'),
        ('r15', 'r17', 'r15-eth4', 'r17-eth1'),
        ('r16', 'r18', 'r16-eth5', 'r18-eth1'),
        ('r17', 'r18', 'r17-eth2', 'r18-eth2'),
    ]
    
    # Calculate number of links to modify
    num_links_to_modify = max(1, int(len(all_links) * percentage / 100))
    
    # Randomly select with seed
    random.seed(seed)
    selected_links = random.sample(all_links, num_links_to_modify)
    
    return selected_links


def apply_asymmetry_to_configs(config_dir, selected_links, low_cost_range, high_cost_range, seed):
    """
    Apply directional asymmetry to selected links by modifying FRR configurations
    using geographic position logic of routers
    """
    # Define actual router positions in topology (vertical pairs)
    router_positions = {
        # Upper level: vertical pairs LEFT-CENTER-RIGHT
        'r1': (0, 0), 'r2': (0, 1),  # left pair
        'r3': (1, 0), 'r4': (1, 1),  # center pair  
        'r5': (2, 0), 'r6': (2, 1),  # right pair
        
        # Middle level: vertical pairs LEFT-CENTER-RIGHT
        'r7': (0, 2), 'r8': (0, 3),   # left pair
        'r9': (1, 2), 'r10': (1, 3),  # center pair
        'r11': (2, 2), 'r12': (2, 3), # right pair
        
        # Lower level: vertical pairs LEFT-CENTER-RIGHT  
        'r13': (0, 4), 'r14': (0, 5), # left pair
        'r15': (1, 4), 'r16': (1, 5), # center pair
        'r17': (2, 4), 'r18': (2, 5)  # right pair
    }
    
    # Extract low and high values from ranges
    low_cost = low_cost_range[0] if len(set(low_cost_range)) == 1 else random.randint(low_cost_range[0], low_cost_range[1])
    high_cost = high_cost_range[0] if len(set(high_cost_range)) == 1 else random.randint(high_cost_range[0], high_cost_range[1])
    
    for rA, rB, intfA, intfB in selected_links:
        if rA not in router_positions or rB not in router_positions:
            continue
            
        pos_a = router_positions[rA]
        pos_b = router_positions[rB]
        
        # Determine if it's horizontal, vertical or diagonal link
        dx = pos_b[0] - pos_a[0]  # X difference (left-right)
        dy = pos_b[1] - pos_a[1]  # Y difference (top-bottom)
        
        # Apply asymmetry to ALL links with directional movement
        if abs(dx) > 0 or abs(dy) > 0:  # Has horizontal OR vertical movement
            
            # Determine costs for horizontal direction
            if dx > 0:  # A is left of B
                cost_horizontal_a_to_b = low_cost   # LEFT→RIGHT: low cost
                cost_horizontal_b_to_a = high_cost  # RIGHT→LEFT: high cost
            elif dx < 0:  # A is right of B
                cost_horizontal_a_to_b = high_cost  # RIGHT→LEFT: high cost
                cost_horizontal_b_to_a = low_cost   # LEFT→RIGHT: low cost
            else:  # dx == 0, no horizontal movement
                cost_horizontal_a_to_b = 0
                cost_horizontal_b_to_a = 0
            
            # Determine costs for vertical direction
            if dy > 0:  # A is above B
                cost_vertical_a_to_b = low_cost   # TOP→BOTTOM: low cost
                cost_vertical_b_to_a = high_cost  # BOTTOM→TOP: high cost
            elif dy < 0:  # A is below B
                cost_vertical_a_to_b = high_cost  # BOTTOM→TOP: high cost
                cost_vertical_b_to_a = low_cost   # TOP→BOTTOM: low cost
            else:  # dy == 0, no vertical movement
                cost_vertical_a_to_b = 0
                cost_vertical_b_to_a = 0
            
            # Combine costs: if there's both horizontal and vertical movement,
            # use higher cost (more restrictive)
            if dx != 0 and dy != 0:  # Diagonal movement
                final_cost_a_to_b = max(cost_horizontal_a_to_b, cost_vertical_a_to_b)
                final_cost_b_to_a = max(cost_horizontal_b_to_a, cost_vertical_b_to_a)
            elif dx != 0:  # Only horizontal movement
                final_cost_a_to_b = cost_horizontal_a_to_b
                final_cost_b_to_a = cost_horizontal_b_to_a
            else:  # Only vertical movement
                final_cost_a_to_b = cost_vertical_a_to_b
                final_cost_b_to_a = cost_vertical_b_to_a
            
            # Modify router A configuration
            _modify_interface_cost(config_dir, rA, intfA, final_cost_a_to_b)
            
            # Modify router B configuration
            _modify_interface_cost(config_dir, rB, intfB, final_cost_b_to_a)


def _modify_interface_cost(config_dir, router_name, interface_name, new_cost):
    """
    Modify OSPF cost of specific interface in frr.conf file
    """
    frr_conf_path = os.path.join(config_dir, router_name, "frr.conf")
    
    if not os.path.exists(frr_conf_path):
        return False
    
    # Read existing file
    with open(frr_conf_path, 'r') as f:
        lines = f.readlines()
    
    # Modify lines related to specific interface
    modified_lines = []
    in_target_interface = False
    
    for line in lines:
        if line.strip() == f"interface {interface_name}":
            in_target_interface = True
            modified_lines.append(line)
        elif in_target_interface and line.strip() == "!":
            # End of interface section
            in_target_interface = False
            modified_lines.append(line)
        elif in_target_interface and line.strip().startswith("ip ospf cost"):
            # Replace cost line
            modified_lines.append(f" ip ospf cost {new_cost}\n")
        else:
            modified_lines.append(line)
    
    # Rewrite file
    with open(frr_conf_path, 'w') as f:
        f.writelines(modified_lines)
    
    return True


def save_traceroutes_raw(net, filename):
    """Execute and save traceroutes between all hosts"""
    hosts = [h for h in net.keys() if h.startswith('h')]
    
    with open(filename, 'w') as f:
        for src in sorted(hosts):
            for dst in sorted(hosts):
                if src != dst:
                    f.write(f"Traceroute from {src} to {dst}:\n")
                    
                    # Connectivity test
                    ping_result = net[src].cmd(f"ping -c 1 -W 2 {net[dst].IP()}")
                    
                    # Execute traceroute
                    result = net[src].cmd(f"traceroute -I -n -m 30 -w 3 {net[dst].IP()}")
                    f.write(result + "\n\n")
                    
                    time.sleep(1)


def run_shell_command(cmd, timeout=120):
    """Execute shell command with error handling"""
    try:
        result = subprocess.run(cmd, shell=True, check=True, timeout=timeout, 
                              capture_output=True, text=True)
        return True, result.stdout
    except subprocess.TimeoutExpired:
        return False, ""
    except subprocess.CalledProcessError as e:
        return False, e.stderr
    except Exception as e:
        return False, str(e)


def copy_configs_to_frr(config_dir):
    """Copy configurations to system FRR directory"""
    copy_commands = []
    for i in range(1, 19):
        router_name = f"r{i}"
        src_file = f"{config_dir}/{router_name}/frr.conf"
        dst_dir = f"/etc/frr/{router_name}"
        dst_file = f"{dst_dir}/frr.conf"
        
        if os.path.exists(src_file):
            copy_commands.extend([
                f"sudo install -m 775 -o frr -g frrvty -d {dst_dir}",
                f"sudo install -m 644 -o frr -g frr {src_file} {dst_file}"
            ])
    
    # Execute all commands
    for cmd in copy_commands:
        success, output = run_shell_command(cmd)
        if not success:
            return False
    
    return True


def restart_frr_routers(net):
    """Restart all FRR routers and wait for convergence"""
    # Stop all routers
    for i in range(1, 19):
        router_name = f"r{i}"
        net[router_name].cmd(f"/usr/lib/frr/frrinit.sh stop {router_name}")
    
    time.sleep(5)
    
    # Restart all routers
    for i in range(1, 19):
        router_name = f"r{i}"
        net[router_name].cmd(f"/usr/lib/frr/frrinit.sh start {router_name}")
    
    # Wait for OSPF convergence
    time.sleep(75)
    
    return True


def create_simulation_directory(sim_number, base_dir="./simulations"):
    """
    Create directory for specific simulation.
    """
    sim_dir = os.path.join(base_dir, f"sim{sim_number}")
    os.makedirs(sim_dir, exist_ok=True)
    return sim_dir


def save_simulation_metadata(sim_dir, sim_number, seed, low_cost_range, high_cost_range, percentages):
    """
    Save simulation metadata to JSON file.
    """
    metadata = {
        "simulation_number": sim_number,
        "timestamp": datetime.now().isoformat(),
        "seed": seed,
        "low_cost_range": low_cost_range,
        "high_cost_range": high_cost_range,
        "asymmetry_percentages": percentages,
        "description": f"Simulation {sim_number} with directional geographic asymmetry, seed {seed}",
        "simulation_type": "directional_geographic_asymmetry",
        "cost_model": "geographic_directional",
        "cost_rules": {
            "left_to_right": "low_cost",
            "right_to_left": "high_cost",
            "top_to_bottom": "low_cost",
            "bottom_to_top": "high_cost"
        }
    }
    
    metadata_file = os.path.join(sim_dir, "simulation_metadata.json")
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)


def run_asymmetry_test_suite_for_simulation(net, sim_dir, sim_number, percentages, seed, 
                                           low_cost_range, high_cost_range):
    """
    Execute complete asymmetry test suite for single simulation
    with directional geographic asymmetry
    """
    results = {}
    
    # Save simulation metadata
    save_simulation_metadata(sim_dir, sim_number, seed, low_cost_range, high_cost_range, percentages)
    
    # Use shared config directory
    config_dir = "./config"
    
    # Test for each asymmetry percentage (INCLUDING 0%)
    for i, percentage in enumerate(percentages):
        # Apply asymmetry configuration
        if percentage == 0:
            # For 0%, apply only baseline configuration
            success = create_ospf_baseline_config(config_dir)
        else:
            # For other percentages, apply directional geographic asymmetry
            if create_ospf_baseline_config(config_dir):
                # Select links for asymmetry
                selected_links = select_links_for_asymmetry(percentage, seed)
                
                # Apply directional geographic asymmetry
                apply_asymmetry_to_configs(config_dir, selected_links, low_cost_range, high_cost_range, seed)
                success = True
            else:
                success = False
        
        if success:
            # Copy configurations to /etc/frr
            if copy_configs_to_frr(config_dir):
                # Restart all FRR routers
                if restart_frr_routers(net):
                    # Execute and save traceroutes in simulation directory
                    filename = os.path.join(sim_dir, f"traceroutes_asymmetry_{percentage}percent.txt")
                    
                    save_traceroutes_raw(net, filename)
                    
                    results[f'{percentage}%'] = filename
                    
    # Save results summary in simulation directory
    results_summary = {
        "simulation_number": sim_number,
        "seed": seed,
        "low_cost_range": low_cost_range,
        "high_cost_range": high_cost_range,
        "percentages_tested": percentages,
        "files_generated": {test_name: os.path.basename(filename) for test_name, filename in results.items()},
        "timestamp": datetime.now().isoformat(),
        "simulation_type": "directional_geographic_asymmetry"
    }
    
    summary_file = os.path.join(sim_dir, "results_summary.json")
    with open(summary_file, 'w') as f:
        json.dump(results_summary, f, indent=2)
    
    return results


def run_multiple_directional_simulations(sim_configs, base_dir="./simulations", percentages=None):
    """
    Execute multiple simulations with different directional geographic configurations.
    
    Args:
        sim_configs: List of dictionaries with configurations for each simulation
                    Format: [{"seed": 123, "low_cost_range": [20,40], "high_cost_range": [100,200]}, ...]
        base_dir: Base directory for simulations
        percentages: List of percentages to test
    
    Returns:
        dict: Results of all simulations
    """
    if percentages is None:
        percentages = [0, 20, 40, 60, 80, 100]
    
    all_results = {}
    
    for sim_number, config in enumerate(sim_configs, 1):
        # Create directory for this simulation
        sim_dir = create_simulation_directory(sim_number, base_dir)
        
        # Start Mininet topology
        topo = NetworkTopo()
        net = Mininet(topo=topo)
        net.start()

        # Assign IP addresses to router interfaces (host-router links)
        for hname, rname, intfName, ip in topo.host_router_links:
            net[rname].setIP(ip, intf=intfName)

        # Assign IP addresses to router interfaces (router-router links)
        for rA, rB, intfA, intfB, ipA, ipB in topo.router_links:
            net[rA].setIP(ipA, intf=intfA)
            net[rB].setIP(ipB, intf=intfB)

        # Start FRR daemons on each router
        for i in range(1, 19):
            router_name = f'r{i}'
            net[router_name].cmd(f"/usr/lib/frr/frrinit.sh start {router_name}")

        time.sleep(10)
        
        # Wait for initial OSPF convergence
        time.sleep(60)
        
        # Execute automatic directional asymmetry tests for this simulation
        try:
            sim_results = run_asymmetry_test_suite_for_simulation(
                net=net,
                sim_dir=sim_dir,
                sim_number=sim_number,
                percentages=percentages,
                seed=config.get('seed'),
                low_cost_range=config.get('low_cost_range', [20, 40]),
                high_cost_range=config.get('high_cost_range', [100, 200])
            )
            
            all_results[f'sim{sim_number}'] = {
                'config': config,
                'sim_dir': sim_dir,
                'results': sim_results
            }
            
        except Exception as e:
            all_results[f'sim{sim_number}'] = {
                'config': config,
                'sim_dir': sim_dir,
                'error': str(e)
            }
        finally:
            # Stop FRR daemons on each router
            for i in range(1, 19):
                router_name = f'r{i}'
                net[router_name].cmd(f"/usr/lib/frr/frrinit.sh stop {router_name}")

            net.stop()
    
    # Save global summary of all simulations
    global_summary = {
        "total_simulations": len(sim_configs),
        "base_directory": base_dir,
        "percentages_tested": percentages,
        "simulation_type": "directional_geographic_asymmetry",
        "cost_model": "geographic_directional",
        "simulations": all_results,
        "timestamp": datetime.now().isoformat()
    }
    
    global_summary_file = os.path.join(base_dir, "global_summary.json")
    os.makedirs(base_dir, exist_ok=True)
    with open(global_summary_file, 'w') as f:
        json.dump(global_summary, f, indent=2)
    
    return all_results


def run_directional_topology(auto_multi_sim=False, sim_configs=None, asymmetry_percentages=None, 
                           single_traceroute=None, base_sim_dir="./simulations"):
    """
    Main function to execute directional geographic asymmetry tests
    """
    
    if auto_multi_sim and sim_configs:
        # Execute multiple simulations
        return run_multiple_directional_simulations(
            sim_configs=sim_configs,
            base_dir=base_sim_dir,
            percentages=asymmetry_percentages
        )
    else:
        # Execute single simulation (original behavior)
        topo = NetworkTopo()
        net = Mininet(topo=topo)
        net.start()

        # Assign IP addresses
        for hname, rname, intfName, ip in topo.host_router_links:
            net[rname].setIP(ip, intf=intfName)

        for rA, rB, intfA, intfB, ipA, ipB in topo.router_links:
            net[rA].setIP(ipA, intf=intfA)
            net[rB].setIP(ipB, intf=intfB)

        # Start FRR daemons
        for i in range(1, 19):
            router_name = f'r{i}'
            net[router_name].cmd(f"/usr/lib/frr/frrinit.sh start {router_name}")

        time.sleep(10)

        try:
            # Wait for initial OSPF convergence
            time.sleep(60)
            
            # Execute single traceroute if requested
            if single_traceroute:
                save_traceroutes_raw(net, single_traceroute)
            
            # Interactive CLI for debug if necessary
            CLI(net)
            
        finally:
            # Cleanup
            for i in range(1, 19):
                router_name = f'r{i}'
                net[router_name].cmd(f"/usr/lib/frr/frrinit.sh stop {router_name}")
            
            net.stop()
        
        return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Advanced runner for directional geographic OSPF asymmetry tests with multiple simulations',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # New parameters for multiple simulations
    parser.add_argument('--multi-sim', action='store_true',
                      help='Execute multiple simulations automatically')
    parser.add_argument('--sim-seeds', type=int, nargs='+',
                      help='List of seeds for each simulation (e.g. --sim-seeds 123 456 789)')
    parser.add_argument('--num-sims', type=int, default=5,
                      help='Number of simulations to execute (default: 5, ignored if --sim-seeds specified)')
    parser.add_argument('--base-sim-dir', type=str, default='./simulations',
                      help='Base directory for simulations (default: ./simulations)')
    
    # Asymmetry parameters (applied to all simulations)
    parser.add_argument('--asymmetry-percentages', type=int, nargs='+',
                      help='Asymmetry percentages to test (e.g. --asymmetry-percentages 0 30 60 100)')
    
    # OSPF COST RANGE PARAMETERS (applied to all simulations if not specified differently)
    parser.add_argument('--low-cost-range', type=int, nargs=2, default=[20, 40],
                      help='Range (min max) for low OSPF costs (default: 20 40)')
    parser.add_argument('--high-cost-range', type=int, nargs=2, default=[100, 200],
                      help='Range (min max) for high OSPF costs (default: 100 200)')
    
    # Legacy parameters (for single simulation)
    parser.add_argument('--single-traceroute', type=str,
                      help='Execute complete traceroute collection and save with specified prefix')
    parser.add_argument('--log-level', type=str, default='info', choices=['debug', 'info', 'warning', 'error'],
                      help='Logging level (default: info)')
    
    args = parser.parse_args()
    
    setLogLevel(args.log_level)
    
    if args.multi_sim:
        # Prepare simulation configurations
        sim_configs = []
        
        if args.sim_seeds:
            # Use specified seeds
            for seed in args.sim_seeds:
                sim_configs.append({
                    'seed': seed,
                    'low_cost_range': args.low_cost_range,
                    'high_cost_range': args.high_cost_range
                })
        else:
            # Generate seeds automatically
            import random
            for i in range(args.num_sims):
                sim_configs.append({
                    'seed': random.randint(1, 10000),
                    'low_cost_range': args.low_cost_range,
                    'high_cost_range': args.high_cost_range
                })
        
        results = run_directional_topology(
            auto_multi_sim=True,
            sim_configs=sim_configs,
            asymmetry_percentages=args.asymmetry_percentages,
            base_sim_dir=args.base_sim_dir
        )
        
    else:
        # Single simulation (original behavior)
        run_directional_topology(
            single_traceroute=args.single_traceroute
        )
