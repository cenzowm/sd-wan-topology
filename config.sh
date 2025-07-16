#!/bin/bash
# Router list
ROUTERS=$(seq 1 18)
# Loop through each router
for ROUTER in $ROUTERS
do
    echo "Configuring router r${ROUTER}..."
    
    # Create log directory for the router
    sudo install -m 775 -o frr -g frr -d /var/log/frr/r${ROUTER}
    
    # Create configuration directory for the router
    sudo install -m 775 -o frr -g frrvty -d /etc/frr/r${ROUTER}
    
    # Copy frr.conf configuration file
    sudo install -m 640 -o frr -g frr config/r${ROUTER}/frr.conf \
        /etc/frr/r${ROUTER}/frr.conf
    
    # Copy daemons file
    sudo install -m 640 -o frr -g frr config/r${ROUTER}/daemons \
        /etc/frr/r${ROUTER}/daemons
    
    # Copy vtysh.conf file
    sudo install -m 640 -o frr -g frrvty config/r${ROUTER}/vtysh.conf \
        /etc/frr/r${ROUTER}/vtysh.conf
    
    # Create vty socket file for each router
    #sudo touch /var/run/frr/r${ROUTER}.vty
    #sudo chown frr:frrvty /var/run/frr/r${ROUTER}.vty
    #sudo chmod 770 /var/run/frr/r${ROUTER}.vty
    echo "Router r${ROUTER} configured successfully."
done
echo "All routers have been configured successfully."
