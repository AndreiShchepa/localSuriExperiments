## Performance tests
### Trex
* run daemon server `sudo ./trex_daemon_server start` 
* Example of configuration file:
```bash
- port_limit : 2 
  version : 2 
  prefix : trex1 
  limit_memory : 1024 
  interfaces : ["0000:04:00.1","0000:04:00.0"] 
  port_info :
    - dest_mac : 00:1b:21:a9:32:00
    - dest_mac : 00:1b:21:a9:32:01
```
### Running
```bash
python3 statistics.py
```
### Requirements
* `lbr_trex_client`:https://gitlab.liberouter.org/testing/trex-client#installation
* `lbr_testsuite`:https://gitlab.liberouter.org/tmc/testsuite#installation-and-dependency-on-lbr_trex_client-package
* matplotlib==3.3.4
* trex-api==0.0.1
* trex-stl-lib==0.3

## suricata-verify 
### Requirements: 
```
sudo ip link add veth0 type veth peer name veth1
sudo ip link set dev veth0 up
sudo ip link set dev veth1 up
```
### Running
```bash
Usage: ./run.py --testdir <path_to_prefilter_tests> --prefilter [--metadata] -j 1
	--testdir - specify the path to the directory with tests
	--prefilter - run program with prefilter support
	--metadata - use prefilter configuration file with turned metadata on. 
				 Should be used in combination with --prefilter
	-j - specify the number of threads
```
#### Error
In case of errror `Error: dpdk: net_pcap0: invalid socket id (err=-1) [DeviceConfigure:runmode-dpdk.c:1681` add `retval = 0` to the line 1680. 
