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
The network topology looks like below:

<img src="./figs/topology.png" title="./figs/topology.png" width=800px></img>

## Run experiments

## open5gs VM

Run the core network topology:
```
sudo python3 core_o5gs4g.py
```
Wait for the remote controller to start

Before running the ran network, the 4g core subscriber information should be updated in the WEBUI using localhost. 
```
http://<open5gs VM IP>:3000/
```

Note: Subsriber informations in the core network should be the same as ue informations set in the ue.conf file of the srsue.

<img src="./figs/webui.png" title="./figs/webui.png" width=800px></img>


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
At this stage the ran components of the srsRAN vm should ping the EPC core in the open5gs vm and vise versa. Beside, log files of both tolology can be seen and tcpdump can also be started to observe the connection. Traffic needs to be sent from the srsRAN first because the remote controller IP is similar to the private IP of srsRAN VM. SO that either the ue or enb should ping the epc core of the open5gs VM.

#### Remark
The project is initially planned to perform S1 handover having two srsENBs and one UE, which is not complete and still needs improvement.

