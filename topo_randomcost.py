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
from datetime import datetime
import re


class LinuxRouter(Node):
    "A Node with IP forwarding enabled."

    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        # Enable IP forwarding on the router
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()


class NetworkTopo(Topo):
    "A LinuxRouter connecting multiple IP subnets"

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

        # Create a list to keep track of host-router links
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

        # Define router-to-router links with explicit interface names
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

        # Add router-to-router links
        for rA, rB, intfA, intfB, ipA, ipB in self.router_links:
            self.addLink(routers[rA], routers[rB], intfName1=intfA, intfName2=intfB)


def create_baseline_frr_configs(config_dir="./config"):
    """
    Create baseline FRR configurations with OSPF cost = 1 for all interfaces.
    This function is completely self-contained and doesn't rely on external scripts.
    """
    # Router links from topology
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

    # Host router links from topology
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
            f.write(f"# Generated automatically - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
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
            
            # Announce networks
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


def generate_random_ospf_costs(percentage=30, seed=42, min_cost=10, max_cost=100):
    """
    Generate random OSPF costs for router links with specified asymmetry percentage.
    Selected links will have DIFFERENT costs on both interfaces.
    ALL other interfaces of ALL routers will have cost = 1.
    
    Returns:
        dict: Dictionary with "router.interface" keys and corresponding OSPF costs as values
    """
    # Initialize random number generator with specified seed
    random.seed(seed)
    
    # Router links from topology
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

    # Host router links from topology
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
    
    # Extract ALL topology interfaces
    all_interfaces = set()
    
    # Add router-router interfaces
    for rA, rB, intfA, intfB, _, _ in router_links:
        all_interfaces.add((rA, intfA))
        all_interfaces.add((rB, intfB))
    
    # Add host-router interfaces
    for _, router, interface, _ in host_router_links:
        all_interfaces.add((router, interface))
    
    # Initialize ALL interfaces with cost = 1
    ospf_costs = {}
    for router, interface in all_interfaces:
        ospf_costs[f"{router}.{interface}"] = 1
    
    # Calculate how many links should be asymmetric
    num_links = len(router_links)
    num_asymmetric_links = int(num_links * percentage / 100)
    
    if num_asymmetric_links == 0:
        return ospf_costs
    
    # Randomly select links to make asymmetric
    links_to_modify = random.sample(range(num_links), num_asymmetric_links)
    
    # For each selected link, apply asymmetric costs
    for link_idx in links_to_modify:
        rA, rB, intfA, intfB, _, _ = router_links[link_idx]
        
        # Generate two DIFFERENT randomized costs for both interfaces
        cost_A = random.randint(min_cost, max_cost)
        
        # Ensure cost_B is different from cost_A
        cost_B = random.randint(min_cost, max_cost)
        while cost_B == cost_A:
            cost_B = random.randint(min_cost, max_cost)
        
        # Overwrite default costs = 1 with asymmetric ones
        ospf_costs[f"{rA}.{intfA}"] = cost_A
        ospf_costs[f"{rB}.{intfB}"] = cost_B
    
    return ospf_costs


def update_frr_configs_with_costs(ospf_costs, config_dir="./config"):
    """
    Update FRR configuration files with specified OSPF costs.
    
    Args:
        ospf_costs: Dictionary with "router.interface" keys and corresponding OSPF costs as values
        config_dir: Configuration directory
        
    Returns:
        List of modified files
    """
    modified_files = []
    
    # Find FRR configuration files
    frr_configs = {}
    for i in range(1, 19):
        router_name = f'r{i}'
        config_path = os.path.join(config_dir, f'r{i}', 'frr.conf')
        
        if os.path.exists(config_path):
            frr_configs[router_name] = config_path
    
    for router_name, config_path in frr_configs.items():
        # Read configuration file
        try:
            with open(config_path, 'r') as f:
                config_content = f.read()
        except Exception as e:
            continue
        
        # Get list of interfaces for this router that should have a cost
        router_interfaces = {}
        for key, cost in ospf_costs.items():
            if key.startswith(f"{router_name}."):
                intf_name = key.split('.')[1]
                router_interfaces[intf_name] = cost
        
        # If no interfaces to modify for this router, skip
        if not router_interfaces:
            continue
        
        # Use regex-based approach to correctly modify OSPF costs
        modified_content = config_content
        
        # First remove all existing OSPF costs
        modified_content = re.sub(r'\s+ip ospf cost \d+', '', modified_content)
        
        # Find all interface sections
        interface_pattern = r'(interface\s+(\S+)(?:\s+.*?)?(?=\n[^\s]|\Z))'
        interfaces_found = []
        
        for interface_match in re.finditer(interface_pattern, config_content, re.DOTALL):
            interface_block = interface_match.group(1)
            interface_name = interface_match.group(2)
            interfaces_found.append(interface_name)
            
            # Skip loopback interface
            if interface_name == 'lo':
                continue
            
            # Check if this interface has custom cost
            if interface_name in router_interfaces:
                cost = router_interfaces[interface_name]
                
                # Remove any existing OSPF costs
                cleaned_block = re.sub(r'\s+ip ospf cost \d+', '', interface_block)
                
                # Add new OSPF cost line
                if cleaned_block.strip().endswith('!'):
                    # If ends with '!', insert before
                    new_block = cleaned_block.rstrip('!').rstrip() + f"\n ip ospf cost {cost}\n!"
                else:
                    # Otherwise, add to end
                    new_block = cleaned_block.rstrip() + f"\n ip ospf cost {cost}"
                
                # Replace original block with modified one
                modified_content = modified_content.replace(interface_block, new_block)
        
        # Write file only if it was modified
        if modified_content != config_content:
            try:
                with open(config_path, 'w') as f:
                    f.write(modified_content)
                modified_files.append(config_path)
            except Exception as e:
                pass
    
    return modified_files


def save_all_traceroutes(net, filename, delay_between_traceroutes=4):
    """
    Save all traceroutes between all hosts in a single TXT file.
    
    Args:
        net: Mininet network
        filename: TXT filename to generate
        delay_between_traceroutes: Delay in seconds between traceroutes
    
    Returns:
        str: Generated filename
    """
    hosts = [h for h in net.keys() if h.startswith('h')]

    with open(filename, 'w') as f:
        for src in hosts:
            for dst in hosts:
                if src != dst:
                    f.write(f"Traceroute from {src} to {dst}:\n")
                    
                    # Connectivity test
                    net[src].cmd(f"ping -c 1 {net[dst].IP()}")

                    # Execute traceroute
                    result = net[src].cmd(f"traceroute -I -n -m 64 {net[dst].IP()}")

                    # Write raw result to file
                    f.write(result + "\n\n")
                    time.sleep(delay_between_traceroutes)
    
    return filename


def run_shell_command(cmd, timeout=120, show_output=False):
    """Execute shell command with error handling."""
    try:
        result = subprocess.run(cmd, shell=True, check=True, timeout=timeout, 
                              capture_output=not show_output, text=True)
        return True
    except subprocess.TimeoutExpired:
        return False
    except subprocess.CalledProcessError as e:
        return False
    except Exception as e:
        return False


def apply_baseline_configuration(config_dir="./config"):
    """
    Apply baseline (symmetric) configuration with OSPF costs = 1.
    This function is now completely self-contained.
    """
    return create_baseline_frr_configs(config_dir)


def apply_asymmetry_configuration_random(percentage, seed=None, min_cost=10, max_cost=100, config_dir="./config"):
    """
    Apply specific asymmetry configuration using internal functions.
    Edges are randomly selected and receive DIFFERENT costs on both interfaces.
    ALL other interfaces of ALL routers maintain cost = 1.
    
    Args:
        percentage: Percentage of links to make asymmetric
        seed: Seed for reproducibility
        min_cost: Minimum OSPF cost
        max_cost: Maximum OSPF cost
        config_dir: Configuration directory
    """
    # First create baseline configuration (all costs = 1)
    if not create_baseline_frr_configs(config_dir):
        return False
    
    # If percentage > 0, apply asymmetry on selected links
    if percentage > 0:
        # Generate OSPF costs with asymmetry
        ospf_costs = generate_random_ospf_costs(
            percentage=percentage,
            seed=seed,
            min_cost=min_cost,
            max_cost=max_cost
        )
        
        # Update configuration files with new costs
        modified_files = update_frr_configs_with_costs(ospf_costs, config_dir)
        
        if not modified_files:
            return False
    
    return True


def copy_configs_to_frr(config_dir="./config"):
    """Copy configurations from config_dir to /etc/frr with correct permissions."""
    copy_cmd = f"""
    for i in $(seq 1 18); do
        if [ -f "{config_dir}/r${{i}}/frr.conf" ]; then
            sudo install -m 775 -o frr -g frrvty -d "/etc/frr/r${{i}}"
            sudo install -m 644 -o frr -g frr "{config_dir}/r${{i}}/frr.conf" "/etc/frr/r${{i}}/frr.conf"
        fi
    done
    """
    
    return run_shell_command(copy_cmd)


def restart_frr_routers(net):
    """Restart all FRR routers in topology and wait for OSPF convergence."""
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
    time.sleep(70)
    
    return True


def create_simulation_directory(sim_number, base_dir="./simulations"):
    """
    Create directory for a specific simulation.
    
    Args:
        sim_number: Simulation number
        base_dir: Base directory for simulations
    
    Returns:
        str: Path of created directory
    """
    sim_dir = os.path.join(base_dir, f"sim{sim_number}")
    os.makedirs(sim_dir, exist_ok=True)
    return sim_dir


def save_simulation_metadata(sim_dir, sim_number, seed, min_cost, max_cost, percentages):
    """
    Save simulation metadata to JSON file.
    
    Args:
        sim_dir: Simulation directory
        sim_number: Simulation number
        seed: Used seed
        min_cost: Minimum OSPF cost
        max_cost: Maximum OSPF cost
        percentages: List of tested percentages
    """
    metadata = {
        "simulation_number": sim_number,
        "timestamp": datetime.now().isoformat(),
        "seed": seed,
        "min_cost": min_cost,
        "max_cost": max_cost,
        "asymmetry_percentages": percentages,
        "description": f"Simulation {sim_number} with random asymmetry, seed {seed}",
        "simulation_type": "random_asymmetry",
        "cost_model": "random_different"
    }
    
    metadata_file = os.path.join(sim_dir, "simulation_metadata.json")
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)


def run_automated_asymmetry_tests_random(net, sim_dir, sim_number, percentages=None, seed=None, min_cost=10, max_cost=100):
    """
    Automatically execute random asymmetry tests with different percentages for a specific simulation.
    
    Args:
        net: Mininet network
        sim_dir: Simulation directory
        sim_number: Simulation number
        percentages: List of percentages to test
        seed: Seed for reproducibility
        min_cost: Minimum OSPF cost
        max_cost: Maximum OSPF cost
    
    Returns:
        dict: Test results with information about generated files
    """
    if percentages is None:
        percentages = [0, 20, 40, 60, 80, 100]
    
    results = {}
    
    # Save simulation metadata
    save_simulation_metadata(sim_dir, sim_number, seed, min_cost, max_cost, percentages)
    
    # Test for each asymmetry percentage
    for i, percentage in enumerate(percentages):
        # Apply asymmetry configuration
        if percentage == 0:
            # For 0%, apply only baseline configuration
            success = apply_baseline_configuration()
        else:
            # For other percentages, apply random asymmetry
            success = apply_asymmetry_configuration_random(
                percentage=percentage, 
                seed=seed, 
                min_cost=min_cost, 
                max_cost=max_cost
            )
        
        if success:
            # Copy configurations to /etc/frr
            if copy_configs_to_frr():
                # Restart all FRR routers
                if restart_frr_routers(net):
                    # Execute and save traceroutes in simulation directory
                    filename = os.path.join(sim_dir, f"traceroutes_asymmetry_{percentage}percent.txt")
                    
                    save_all_traceroutes(
                        net=net, 
                        filename=filename,
                        delay_between_traceroutes=4
                    )
                    
                    results[f'{percentage}%'] = filename
    
    # Save results summary in simulation directory
    results_summary = {
        "simulation_number": sim_number,
        "seed": seed,
        "min_cost": min_cost,
        "max_cost": max_cost,
        "percentages_tested": percentages,
        "files_generated": {test_name: os.path.basename(filename) for test_name, filename in results.items()},
        "timestamp": datetime.now().isoformat(),
        "simulation_type": "random_asymmetry"
    }
    
    summary_file = os.path.join(sim_dir, "results_summary.json")
    with open(summary_file, 'w') as f:
        json.dump(results_summary, f, indent=2)
    
    return results


def run_multiple_simulations(sim_configs, base_dir="./simulations", percentages=None):
    """
    Execute multiple simulations with different configurations.
    
    Args:
        sim_configs: List of dictionaries with configurations for each simulation
                    Format: [{"seed": 123, "min_cost": 10, "max_cost": 100}, ...]
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
        
        # Execute automatic asymmetry tests for this simulation
        try:
            sim_results = run_automated_asymmetry_tests_random(
                net=net,
                sim_dir=sim_dir,
                sim_number=sim_number,
                percentages=percentages,
                seed=config.get('seed'),
                min_cost=config.get('min_cost', 10),
                max_cost=config.get('max_cost', 100)
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
        "simulation_type": "random_asymmetry",
        "cost_model": "random_different", 
        "simulations": all_results,
        "timestamp": datetime.now().isoformat()
    }
    
    global_summary_file = os.path.join(base_dir, "global_summary.json")
    os.makedirs(base_dir, exist_ok=True)
    with open(global_summary_file, 'w') as f:
        json.dump(global_summary, f, indent=2)
    
    return all_results


def run(auto_multi_sim=False, sim_configs=None, asymmetry_percentages=None, 
        single_traceroute=None, base_sim_dir="./simulations"):
    """
    Run the network with FRR and optional automated multiple simulations.
    
    Args:
        auto_multi_sim: If True, automatically execute multiple simulations
        sim_configs: List of configurations for simulations
        asymmetry_percentages: List of percentages to test
        single_traceroute: If specified, execute traceroute collection with this prefix
        base_sim_dir: Base directory for simulations
    """
    
    if auto_multi_sim and sim_configs:
        # Execute multiple simulations
        return run_multiple_simulations(
            sim_configs=sim_configs,
            base_dir=base_sim_dir,
            percentages=asymmetry_percentages
        )
    else:
        # Execute single simulation (original behavior)
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
        
        try:
            # Execute single traceroute if requested
            if single_traceroute:
                save_all_traceroutes(net, single_traceroute, delay_between_traceroutes=4)
            
            # Interactive CLI for optional debugging
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
        description='Independent SD-WAN network with automated multiple simulation tests',
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
    
    # OSPF COST PARAMETERS (applied to all simulations)
    parser.add_argument('--min-cost', type=int, default=10,
                      help='Minimum OSPF cost for asymmetric links (default: 10)')
    parser.add_argument('--max-cost', type=int, default=100,
                      help='Maximum OSPF cost for asymmetric links (default: 100)')
    
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
                    'min_cost': args.min_cost,
                    'max_cost': args.max_cost
                })
        else:
            # Generate seeds automatically
            import random
            for i in range(args.num_sims):
                sim_configs.append({
                    'seed': random.randint(1, 10000),
                    'min_cost': args.min_cost,
                    'max_cost': args.max_cost
                })
        
        results = run(
            auto_multi_sim=True,
            sim_configs=sim_configs,
            asymmetry_percentages=args.asymmetry_percentages,
            base_sim_dir=args.base_sim_dir
        )
        
    else:
        # Single simulation (original behavior)
        run(
            single_traceroute=args.single_traceroute
        )
