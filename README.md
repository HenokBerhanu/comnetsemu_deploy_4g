# comnetsemu_deploy_4g

This project is intended for deploying a 4G network on comnetsemu emulator. 
It is done using srsRAN and open5GS
O-RAN alliance introduces a new srsgnb in srsRAN and the RAN part is taken from srsRAN
for the core part, i take open5gs epc core 
The network is deployed on one single VM

## Core part
Emulate a 5G network deployment in comnetsemu.
Demonstrate distributed UPF deployment and slice-base UPF selection.

Tested Versions:
- Comnetsemu: v0.3.0 (Installed following either "Option 1" or "Option 3" from [here](https://git.comnets.net/public-repo/comnetsemu) )
- UERANSIM: v3.2.6
- Open5gs: v2.4.2

Python packages:
- pymongo
- json

## Build Instructions

Clone repository in the comnetsemu VM.

Build the necessary docker images:

```
cd build
./build.sh
```

Or alternatively download them from DockerHub

```
cd ../open5gs
./dockerhub_pull.sh
```


## Run experiments

### Start the network topology:

#### Running example1.py
```
$ sudo python3 example1.py
```

The scenario includes 5 DockerHosts as shown in the figure below.
The UE starts two PDU session one for each slice defined in the core network.

<img src="./images/topology.jpg" title="./images/topology.jpg" width=1000px></img>

Notice that at the first run the set-up should not work due to missing information in the 5GC.
To configure it we should leverage the WebUI by opening the following page in a browser on the host OS.
```
http://<VM_IP>:3000/
```

The configuration is as follows:

UE information:
- IMSI = 001011234567895
- USIM Type = OP
- Operator Key (OPc/OP) = 11111111111111111111111111111111
- key: '8baf473f2f8fd09487cccbd7097c6862'

Slice 1 configuration
- SST: 1
- SD: 000001
- DNN: internet
- Session-AMBR Downlink: 2 Mbps
- Session-AMBR Uplink: 2 Mbps

Slice 2 configuration
- SST: 2
- SD: 000001
- DNN: mec
- Session-AMBR Downlink: 10 Mbps
- Session-AMBR Uplink: 10 Mbps

The configuration should look like this:

<img src="./images/WebUI_config.JPG" title="./images/WebUI_config.JPG" width=800px></img>

You can now proceed testing the environment as below


#### Running example2.py
This example creates the same environment of example1.py but the open5GS control plane configuration is done programmatically without using the webUI. (Note: adapted the python class in the open5gs repo [here](https://github.com/open5gs/open5gs/blob/main/misc/db/python/Open5GS.py) )

Disclaimer: all the previous subcribers registered with the webUI will be lost and a new one will be created.

```
$ sudo python3 example2.py
```



### Check UE connections

Notice how the UE DockerHost has been initiated running `open5gs_ue_init.sh` which, based on the configuration provided in `open5gs-ue.yaml`, creates two default UE connections.
The sessions are started specifying the slice, not the APN. The APN, and thus the associated UPF, is selected by the 5GC since, in `subscriber_profile.json`, a slice is associated to a session with specific DNN.

Enter the container and verify UE connections:

``` 
$ ./enter_container.sh ue

# ifconfig
``` 

You should see interfaces uesimtun0 (for the upf_cld) and uesimtun1 (for the upf_mec) active.

```
uesimtun0: flags=369<UP,POINTOPOINT,NOTRAILERS,RUNNING,PROMISC>  mtu 1400
        inet 10.45.0.2  netmask 255.255.255.255  destination 10.45.0.2
        unspec 00-00-00-00-00-00-00-00-00-00-00-00-00-00-00-00  txqueuelen 500  (UNSPEC)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

uesimtun1: flags=369<UP,POINTOPOINT,NOTRAILERS,RUNNING,PROMISC>  mtu 1400
        inet 10.46.0.2  netmask 255.255.255.255  destination 10.46.0.2
        unspec 00-00-00-00-00-00-00-00-00-00-00-00-00-00-00-00  txqueuelen 500  (UNSPEC)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```


Start a ping test to check connectivity:
``` 
# ping -c 3 -n -I uesimtun0 www.google.com
# ping -c 3 -n -I uesimtun1 www.google.com
``` 

### Test the environment

In two terminals start two tcpdump for both upf_cld and upf_mec

``` 
$ ./start_tcpdump.sh upf_cld
$ ./start_tcpdump.sh upf_mec
``` 

#### Latency test
Enter in the UE container:
``` 
$ ./enter_container.sh ue
``` 

Start ping test on the interfaces related to the two slices:
``` 
# ping -c 3 -n -I uesimtun0 10.45.0.1
# ping -c 3 -n -I uesimtun1 10.46.0.1
``` 

Observe the Round Trip Time using uesimtun0 (slice 1 - reaching the UPF in the "cloud DC" with DNN="internet" ) and ueransim1 (slice 2 - reaching the UPF in the 'mec DC' with DNN="mec")


#### Bandwidth test

Enter in the UE container:
``` 
$ ./enter_container.sh ue
``` 

Start bandwidth test leveraging the two slices:
``` 
# iperf3 -c 10.45.0.1 -B 10.45.0.2 -t 5
# iperf3 -c 10.46.0.1 -B 10.46.0.2 -t 5
``` 

Observe how the data-rate in the two cases follows the maximum data-rate specified for the two slices (2 Mbps for sst 1 and 10Mbps for sst 2).


#### Change the maximum bit-rate available for one slice:

Here we change the slice profiles updating the maximum bit-rate and observe the results on the iperf test.

##### Alternative 1
Open the open5gs WebUI and change the DL/UL bandwidth as follows:
- for sst 1: MBR DL/UL = 10 Mbps
- for sst 2: MBR DL/UL = 20 Mbps

##### Alternative 2
Run the script `update_subscribers.py`.

##### Test new connections

Enter in the UE container:
``` 
$ ./enter_container.sh ue
``` 

Start new PDU sessions in the UE: 

```
# ./nr-cli imsi-001011234567895
$ ps-establish IPv4 --sst 1 --sd 1
$ ps-establish IPv4 --sst 2 --sd 1
$ status
```

Now you should see 4 interfaces `uesimtun1-4` created. This is because the old UE connections are kept with the previous settings as long as we do not remove them.

Start again a bandwidth test in the UE leveraging the new PDU session. NB: use the IPs of the inferfaces for the new sessions (`uesimtun3` and `uesimtun4`):

``` 
iperf3 -c 10.45.0.1 -B 10.45.0.3 -t 5
iperf3 -c 10.46.0.1 -B 10.46.0.3 -t 5
```

From the results you should observe that the achieved bit-rate have changed accordingly to the new setting. 


### Contact

Main maintainer:
- Riccardo Fedrizzi - rfedrizzi@fbk.eu

## RAN part


# comnetsemu + srsRAN
This project aims to integrate a source build of [srsRAN](https://github.com/srsran/srsRAN) in [comnetsemu](https://git.comnets.net/public-repo/comnetsemu/-/tree/master).
Radio packets are exchanged through ZeroMQ instead of a physical radio device (see [srsRAN documentation](https://docs.srsran.com/en/latest/app_notes/source/zeromq/source/index.html) for more information).

### Knowledge base
- `srsENB` supports only one UE per channel (each channel is a ZeroMQ rx/tx pair) as per [official documentation](https://docs.srsran.com/en/latest/app_notes/source/zeromq/source/index.html#known-issues). Since the rx/tx is implemented as a simple [REQ/REP pair](https://zguide.zeromq.org/docs/chapter1/#Ask-and-Ye-Shall-Receive), either:
  - a custom broker based on something like [zeromq/Malamute](https://github.com/zeromq/malamute) has to be used
  - some tricks can be done by changing `tx_type` and `rx_type` to PUB-SUB in `rf.device_args` like this: `--rf.device_args="tx_type=pub,rx_type=sub"` (this is an **undocumented feature** of srsRAN's ZeroMQ radio implementation, found [in the source code here](https://github.com/srsran/srsRAN/blob/5275f33360f1b3f1ee8d1c4d9ae951ac7c4ecd4e/lib/src/phy/rf/rf_zmq_imp.c#L248-L278))
  - the ZeroMQ implementation inside srsRAN must be refactored to support more complex patterns (which will probably never be done since it's outside the scope of the project)
- A single UE can use multiple channels for things like [5G NSA mode](https://docs.srsran.com/en/latest/app_notes/source/5g_nsa_zmq/source/index.html) (implemented in this project).
- Multiple cells can be emulated via [S1 handover](https://docs.srslte.com/en/latest/app_notes/source/handover/source/index.html).

### Development
This project uses a custom build script written in Bash (`make.sh`). The script serves as a replacement for Makefiles (it provides useful command line help and other functionalities) and is self-documenting.
For more information see:
```
$ ./make.sh --help
```

#### Updating `comnetsemu`
If a new version of `comnetsemu` is available, just run
```
$ ./make.sh git_submodules
```

or (basically the same):
```
$ git submodule update --recursive --remote
```

#### Notes on local development (on the host)
> Note: running topology code on the host is kinda useless, so don't do it

To enable code completion in editors and general testing, a Python `virtualenv` is recommended. It can be automatically setup using `./make.sh virtualenv`.

### Project structure
The root directory contains the following files (generally):

| Filename           | Description                                                             |
| ------------------ | ----------------------------------------------------------------------- |
| `comnetsemu/`      | Git submodule linked to the comnetsemu repository                       |
| `comnetsemu-docs/` | HTML documentation compiled from comnetsemu                             |
| `config/`          | srsRAN configuration files. Used as a Docker volume inside the VM       |
| `docker`           | `docker-compose` versions of the network stacks and srsRAN build file   |
| `logs/`            | Will be mounted as a volume inside the srsRAN containers and store logs |
| `slides/`          | Slides and assets                                                       |
| `src/`             | Python scripts with network implementations                             |
| `utils/`           | Contains extra utility files and bash functions for `make.sh`           |
| `README.md`        | This file                                                               |
| `make.sh`          | Build script for this project                                           |
| `Vagrantfile`      | comnetsemu-compatible VM, extend from the original Vagrantfile          |

All other directories/files are either temporary or self-explanatory, e.g.:
- `build/`: contains build artifacts (archives, binaries, whatever's needed at runtime)
- `env/`: Python virtualenv (see section above)



