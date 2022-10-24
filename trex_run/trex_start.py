import lbr_trex_client.paths
from trex.astf.api import *
from trex_client import CTRexClient
import json
import sys

# Connect to TRex daemon
trex_daemon_handler = CTRexClient(trex_host='localhost', trex_daemon_port=8090)

# Acquire TRex by force if needed
trex_daemon_handler.force_kill(confirm=False)

# Start stateful TRex
trex_daemon_handler.start_astf(cfg='/etc/trex_cfg.yaml')

# Connect to TRex
trex_handler = ASTFClient(server='localhost', sync_port=4501, async_port=4500)
trex_handler.connect()

# Acquire ports
trex_handler.reset()

def create_htt4_profile():
    """ 
    Create IPv4/TCP/HTTP profile (1000CPS)
    """ 

    http_req = (
        b'GET /3384 HTTP/1.1\r\nHost: 22.0.0.3\r\nConnection: Keep-Alive\r\nUser-Agent: Mozilla/4.0' +
        b'(compatible; MSIE 7.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)\r\nAccept: */*\r\n' +
        b'Accept-Language: en-us\r\nAccept-Encoding: gzip, deflate, compress\r\n\r\n')
    http_response = (
        'HTTP/1.1 200 OK\r\nServer: Microsoft-IIS/6.0\r\nContent-Type: text/html\r\nContent-Length: ' +
        '32000\r\n\r\n<html>&lt;pre&gt;**********&lt;/pre&gt;&lt;/html&gt;')

    # Client
    prog_c = ASTFProgram(side='c')
    prog_c.connect()                       # Establish TCP connection
    prog_c.send(http_req)
    prog_c.recv(len(http_response))
                                           # Implicit TCP close()

    # Server
    prog_s = ASTFProgram(side='s')
    prog_s.accept()                        # Wait for TCP connection
    prog_s.recv(len(http_req))
    prog_s.send(http_response)

    # Set some global info parameters for client
    c_glob_info = ASTFGlobalInfo()
    c_glob_info.tcp.rxbufsize = 32768
    c_glob_info.tcp.txbufsize = 32768
    c_glob_info.tcp.blackhole=0
    c_glob_info.tcp.keepinit=10
    c_glob_info.tcp.keepidle=10
    c_glob_info.tcp.keepintvl=10

    # Set some global info parameters for server
    s_glob_info = ASTFGlobalInfo()
    s_glob_info.tcp.rxbufsize = 32768
    s_glob_info.tcp.txbufsize = 32768
    s_glob_info.tcp.blackhole=0
    s_glob_info.tcp.keepinit=10
    s_glob_info.tcp.keepidle=10
    s_glob_info.tcp.keepintvl=10
    s_glob_info.ip.dont_use_inbound_mac=0

    # Set IPv4 address range for client
    ip_gen_c = ASTFIPGenDist(ip_range=["10.0.0.1", "10.0.0.254"], distribution="rand")
    # Set IPv4 address range for server
    ip_gen_s = ASTFIPGenDist(ip_range=["10.0.1.1", "10.0.1.62"], distribution="rand")
    ip_gen = ASTFIPGen(glob=ASTFIPGenGlobal(ip_offset="1.0.0.0"), dist_client=ip_gen_c, dist_server=ip_gen_s)

    temp_c = ASTFTCPClientTemplate(program=prog_c, ip_gen=ip_gen, port=80, cps=1000)
    temp_s = ASTFTCPServerTemplate(program=prog_s)
    template = ASTFTemplate(client_template=temp_c, server_template=temp_s)

    return ASTFProfile(default_ip_gen=ip_gen, templates=template, default_c_glob_info=c_glob_info, default_s_glob_info=s_glob_info)

################################################
trex_handler.load_profile(create_htt4_profile())

trex_handler.start(duration=5)
trex_handler.start_latency()

trex_handler.update_latency(100)

trex_handler.wait_on_traffic()
trex_handler.stop_latency()

stats = trex_handler.get_stats()
print(json.dumps(stats, indent=4))

with open(sys.argv[1], 'w') as f:
    print(json.dumps(stats, indent=4), file=f)
################################################

cpu_cores_count = len(trex_handler.get_port_attr(0)['cores'])

# Stop and disconnect from TRex
trex_handler.disconnect()
trex_daemon_handler.stop_trex()

# Basic assert to ensure connections between client (port 0) and server (port 1) were successfully established
# Ensure 1) client connection attempts is equal to client established connections (all attempts succeeded)
#        2) server received connection attempts is equal to server established connections (all attempts from client succeeded)
#        3) connection attempts/established connections is equal to 1000 (CPS) * 10 (duration) connections (+/- cpu_cores_count)
assert stats['traffic']['client']['tcps_connattempt'] == stats['traffic']['client']['tcps_connects']
assert 1000 * 10 - cpu_cores_count <=  stats['traffic']['client']['tcps_connects'] <= 1000 * 10 + cpu_cores_count

assert stats['traffic']['server']['tcps_accepts'] == stats['traffic']['server']['tcps_connects']
assert 1000 * 10 - cpu_cores_count <=  stats['traffic']['server']['tcps_connects'] <= 1000 * 10 + cpu_cores_count
