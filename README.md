# SD-WAN Network Topology Emulation with Mininet and FRR

This repository contains Python scripts for creating and configuring SD-WAN network topologies using Mininet and FRR (Free Range Routing). The scripts provide automated setup of complex network scenarios with configurable OSPF routing asymmetry for traceroute data collection.

## Table of Contents

- [Overview](#overview)
- [Network Topology](#network-topology)
- [Requirements](#requirements)
- [File Descriptions](#file-descriptions)
- [Installation and Setup](#installation-and-setup)
- [Usage Examples](#usage-examples)
- [Configuration Details](#configuration-details)
- [Troubleshooting](#troubleshooting)

## Overview

These scripts create a realistic SD-WAN network topology with 18 routers and 12 hosts using Mininet emulation. The primary purpose is to generate network environments with different OSPF cost configurations to collect traceroute data under various routing scenarios.

### Key Features

- **18-router, 12-host topology** representing enterprise SD-WAN scenarios
- **Automated FRR/OSPF configuration** generation and deployment
- **Multiple asymmetry models** for different routing cost patterns
- **Batch simulation support** for automated data collection
- **Traceroute data collection** between all host pairs

## Network Topology

The emulated network consists of:

```
18 Routers: r1, r2, ..., r18
12 Hosts: h11, h12, h13, h14, h22, h23, h24, h25, h33, h34, h35, h36
```

### Network Architecture

- **Host Networks**: /24 subnets (10.0.11.0/24, 10.0.12.0/24, etc.)
- **Router-Router Links**: /30 point-to-point subnets
- **Network Segments**: 
  - 10.0.1.x (tier 1 interconnections)
  - 10.0.2.x (tier 2 interconnections)  
  - 10.0.3.x (tier 3 interconnections)
  - 10.0.4.x-10.0.8.x (inter-tier connections)

## Requirements

### System Requirements

- **Operating System**: Ubuntu 22.04 LTS or later
- **Python**: 3.8 or higher
- **Privileges**: sudo access required
- **Memory**: Minimum 4GB RAM (8GB recommended for multiple simulations)

### Required Packages

```bash
# System packages
sudo apt update
sudo apt install -y python3 python3-pip mininet frr traceroute
```

## File Descriptions

### `topo_directional.py`
**Main script for directional geographic OSPF asymmetry**

- **Type**: Executable Python script
- **Dependencies**: mininet, frr, json, argparse, random, datetime
- **Purpose**: Creates network topology with directional cost asymmetry based on router geographic positioning

**Key Functions**:
- `NetworkTopo`: Defines complete 18-router topology with explicit interface naming
- `LinuxRouter`: Custom router class with IP forwarding enabled
- `create_ospf_baseline_config()`: Generates FRR configuration files with OSPF settings
- `apply_asymmetry_to_configs()`: Applies directional cost rules (left→right and top→bottom = low cost, reverse = high cost)
- `run_multiple_directional_simulations()`: Executes batch simulations with different parameters

**Asymmetry Logic**:
- Router positions are mapped to a 3x6 grid
- Horizontal movement: left→right = low cost, right→left = high cost
- Vertical movement: top→bottom = low cost, bottom→top = high cost
- Diagonal links use the higher cost of horizontal and vertical components

### `topo_randomcost.py`
**Alternative script for random OSPF cost asymmetry**

- **Type**: Executable Python script  
- **Dependencies**: mininet, frr, json, argparse, random, datetime, re
- **Purpose**: Creates identical network topology with random cost assignment for asymmetric routing

**Key Functions**:
- `NetworkTopo`: Same topology definition as directional version
- `generate_random_ospf_costs()`: Randomly selects links and assigns different costs to each interface
- `update_frr_configs_with_costs()`: Uses regex to modify FRR configuration files
- `run_multiple_simulations()`: Batch execution with random cost parameters

**Asymmetry Logic**:
- Randomly selects percentage of links to make asymmetric
- Assigns different random costs to both interfaces of selected links
- All other interfaces maintain default cost = 1

### `topo.py`
**Basic topology script without asymmetry features**

- **Type**: Executable Python script
- **Dependencies**: mininet, json, time
- **Purpose**: Core topology definition for manual testing and validation

**Key Functions**:
- `NetworkTopo`: Basic 18-router, 12-host topology
- `save_traceroutes_raw()`: Manual traceroute collection to text file
- `save_traceroutes_json()`: Manual traceroute collection to JSON format
- Interactive CLI access for network exploration

### `config.sh`
**FRR configuration deployment script**

- **Type**: Bash shell script
- **Dependencies**: sudo privileges, FRR installation
- **Purpose**: Automates FRR configuration file deployment for all 18 routers

**Functions**:
- Creates FRR directories with correct permissions
- Copies configuration files to system FRR paths
- Sets up logging infrastructure for each router

## Installation and Setup

### 1. System Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip mininet frr traceroute git
```

### 2. FRR Setup

```bash
# Enable and start FRR
sudo systemctl enable frr
sudo systemctl start frr

# Verify installation
sudo systemctl status frr
```

### 3. Clone and Setup

```bash
# Clone repository
git clone <repository-url>
cd sd-wan-topology-emulation

# Make scripts executable
chmod +x topo_directional.py topo_randomcost.py topo.py config.sh

# Create directories
mkdir -p simulations config
```

### 4. User Permissions

```bash
# Add user to FRR groups
sudo usermod -a -G frr,frrvty $USER
# Logout and login for changes to take effect
```

## Usage Examples

### Single Simulation Execution

#### Directional Geographic Asymmetry
```bash
# Basic single run with traceroute collection
sudo python3 topo_directional.py --single-traceroute output_traceroutes.txt
```

#### Random Cost Asymmetry  
```bash
# Basic single run
sudo python3 topo_randomcost.py --single-traceroute random_output.txt
```

#### Basic Topology
```bash
# Simple topology without asymmetry
sudo python3 topo.py
```

### Batch Simulation Execution

#### Multiple Directional Simulations
```bash
# Run 5 simulations with automatic seed generation
sudo python3 topo_directional.py \
    --multi-sim \
    --num-sims 5 \
    --asymmetry-percentages 0 20 40 60 80 100 \
    --low-cost-range 20 40 \
    --high-cost-range 100 200 \
    --base-sim-dir ./simulations/directional

# Run with specific seeds for reproducibility
sudo python3 topo_directional.py \
    --multi-sim \
    --sim-seeds 123 456 789 \
    --asymmetry-percentages 0 30 60 100 \
    --low-cost-range 10 30 \
    --high-cost-range 80 150
```

#### Multiple Random Cost Simulations
```bash
# Run random cost simulations
sudo python3 topo_randomcost.py \
    --multi-sim \
    --sim-seeds 111 222 333 \
    --asymmetry-percentages 0 25 50 75 100 \
    --min-cost 15 \
    --max-cost 120 \
    --base-sim-dir ./simulations/random
```

### Parameter Descriptions

#### Common Parameters
- `--multi-sim`: Enable batch simulation mode instead of single run
- `--sim-seeds LIST`: Specify exact seeds for reproducible results
- `--num-sims NUMBER`: Number of simulations (used if seeds not specified)
- `--asymmetry-percentages LIST`: Percentages of links to make asymmetric (0-100)
- `--base-sim-dir PATH`: Base directory for simulation output files
- `--single-traceroute FILE`: Run single simulation and save traceroutes to file

#### Directional-Specific Parameters
- `--low-cost-range MIN MAX`: Cost range for favorable direction (e.g., left→right)
- `--high-cost-range MIN MAX`: Cost range for unfavorable direction (e.g., right→left)

#### Random-Specific Parameters  
- `--min-cost NUMBER`: Minimum OSPF cost for asymmetric links
- `--max-cost NUMBER`: Maximum OSPF cost for asymmetric links

## Configuration Details

### OSPF Configuration Generation

Both directional and random scripts automatically generate FRR configuration files:

```
config/
├── r1/frr.conf
├── r2/frr.conf  
├── ...
└── r18/frr.conf
```

Each configuration includes:
- Interface IP address assignments
- OSPF area 0 configuration  
- Router-ID assignment
- Network advertisements
- Interface-specific OSPF costs

### Simulation Workflow

1. **Network Creation**: Initialize Mininet topology with 18 routers and 12 hosts
2. **IP Assignment**: Configure all interface IP addresses  
3. **FRR Startup**: Start OSPF daemons on all routers
4. **Configuration**: Apply OSPF costs based on selected asymmetry model
5. **Convergence**: Wait 70-75 seconds for OSPF convergence
6. **Data Collection**: Execute traceroutes between all host pairs
7. **Storage**: Save traceroute output and configuration metadata

### Output Structure

```
simulations/
├── global_summary.json          # Batch simulation summary
├── sim1/
│   ├── simulation_metadata.json # Simulation parameters
│   ├── results_summary.json     # File listing
│   ├── traceroutes_asymmetry_0percent.txt
│   ├── traceroutes_asymmetry_20percent.txt
│   └── ... (other percentages)
├── sim2/
└── ...
```

### Traceroute Output Format

Each traceroute file contains:
```
Traceroute from h11 to h12:
traceroute to 10.0.12.100 (10.0.12.100), 30 hops max, 60 byte packets
 1  10.0.11.10  0.147 ms  0.043 ms  0.033 ms
 2  10.0.1.2  0.159 ms  0.098 ms  0.089 ms
 3  10.0.12.10  0.187 ms  0.139 ms  0.131 ms

Traceroute from h11 to h13:
...
```

## License

This project is part of academic research conducted at Università degli Studi di Milano-Bicocca. Please cite appropriately if using this work in academic publications.

## Citation

```bibtex
@mastersthesis{vommaro2025sdwantopology,
  title={Topology Reconstruction in SD-WAN Using Advanced Network Tomography},
  author={Vommaro Marincola, Vincenzo},
  year={2025},
  school={Università degli Studi di Milano-Bicocca},
  type={Master's thesis}
}
```

## Contact

For questions or collaboration inquiries, please contact:
- **Author**: Vincenzo Vommaro Marincola (cenzowm@gmail.com)
- **Supervisor**: Prof. Marco Savi (marco.savi@unimib.it)
- **Institution**: Università degli Studi di Milano-Bicocca
