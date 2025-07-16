#!/usr/bin/python3

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
import time
import json


class LinuxRouter(Node):
    """A Node with IP forwarding enabled."""

    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        # Enable IP forwarding on the router
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        # Cleanup IP forwarding to prevent routing loops during teardown
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()


class NetworkTopo(Topo):
    """A LinuxRouter connecting multiple IP subnets"""

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
        # Edge network configuration - /24 subnets
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
        # Network segmentation: 10.0.1.x (tier 1), 10.0.2.x (tier 2), 10.0.3.x (tier 3)
        # Inter-tier links use 10.0.4.x-10.0.8.x for path diversity
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
            

def save_traceroutes_raw(net, filename="traceroutes.txt"):
  
    hosts = [h for h in net.keys() if h.startswith('h')]  # Solo host

    with open(filename, 'w') as f:
        for src in hosts:
            for dst in hosts:
                if src != dst:
                    f.write(f"Traceroute from {src} to {dst}:\n")
                    info(f"Traceroute from {src} to {dst}\n")
                    
                 
                    # Connectivity pre-check reduces failed traceroute attempts
                    net[src].cmd(f"ping -c 1 {net[dst].IP()}")

                   
                    # -I flag uses ICMP instead of UDP
                    # -n flag avoids DNS lookups which can skew timing measurements
                    # -m 64 accommodates networks
                    result = net[src].cmd(f"traceroute -I -n -m 64 {net[dst].IP()}")

                    # Write on file
                    f.write(result + "\n\n")
                    # 4-second delay 
                    time.sleep(4)  

    info(f"Traceroutes salvati in {filename}\n")
           
    
def save_traceroutes_json(net, filename="traceroutes"):
 
    hosts = [h for h in net.keys() if h.startswith('h')]  # Solo host
    traceroutes = {}

    for src in hosts:
        traceroutes[src] = {}
        for dst in hosts:
            if src != dst:
                info(f"Traceroute from {src} to {dst}\n")
                    result = net[src].cmd(f"traceroute -I -n -m 64 {net[dst].IP()}")
                hops = []
                for line in result.splitlines()[1:]:
                    parts = line.split()
                    if len(parts) >= 2:
                        hops.append(parts[1])  
                traceroutes[src][dst] = {
                    "path": hops,
                    "hops": len(hops)
                }
               
                time.sleep(4)

   
    with open(filename, 'w') as f:
        json.dump(traceroutes, f, indent=4)
    info(f"Traceroutes salvati in {filename}\n")



def run():
    """Run the network with FRR"""
    topo = NetworkTopo()
    net = Mininet(topo=topo)
    net.start()

    # Assign IP addresses to router interfaces (host-router links)
    # Manual IP assignment required since Mininet doesn't handle multi-interface routers
    for hname, rname, intfName, ip in topo.host_router_links:
        net[rname].setIP(ip, intf=intfName)

    # Assign IP addresses to router interfaces (router-router links)
    # Point-to-point interface configuration
    for rA, rB, intfA, intfB, ipA, ipB in topo.router_links:
        net[rA].setIP(ipA, intf=intfA)
        net[rB].setIP(ipB, intf=intfB)

    # Start FRR daemons on each router
    for i in range(1, 19):
        router_name = f'r{i}'
        info(f"Starting FRR on {router_name}\n")
        net[router_name].cmd(f"/usr/lib/frr/frrinit.sh start {router_name}")

    # Wait for FRR daemons to start
    time.sleep(5)

    # Optionally, display routing tables
    # Useful for debugging
    for i in range(1, 19):
        router_name = f'r{i}'
        info(f"*** Routing Table on {router_name}:\n")
        info(net[router_name].cmd("ip route"))

    CLI(net)

    # Stop FRR daemons on each router
    for i in range(1, 19):
        router_name = f'r{i}'
        info(f"Stopping FRR on {router_name}\n")
        net[router_name].cmd(f"/usr/lib/frr/frrinit.sh stop {router_name}")

    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
