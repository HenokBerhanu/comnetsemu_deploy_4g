# comnetsemu_deploy_4g

This project is intended for deploying a 4G network on comnetsemu emulator. 

It is done using srsRAN and open5GS deployed on two different VMs. The two networks are connected using linux GRE tunnel.

## EPC core
Emulate a 4G network by building open5gs docker image in comnetsemu (open5gs VM). Private VM IP used 192.168.56.102

## srsRAN 
Build docker image for srsENB and srsUE in comnetsemu (srsRAN VM). Private VM IP used 192.168.56.101

## Instructions

Clone repository in the comnetsemu VM.

Build the docker images:

```
For EPC core
cd build
./buildo5gs.sh
```
```
For srsRAN
cd build
./srsbuild3.sh
```

## Run experiments

## open5gs VM

Run the core network topology:
```
sudo python3 core_o5gs4g.py
```
Wait for the remote controller to start

## srsRAN VM

Run the ran network topology:
```
sudo python3 ran_srsran4g.py
```
Wait for the remote controller to start

## Start the remote controller in the srsRAN VM

Starting the controller:
```
sudo controller -v ptcp:6633
```
