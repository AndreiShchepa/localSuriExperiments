#!/bin/bash

mypwd=$(pwd)

[ ! -d /opt/trex ] && mkdir -p /opt/trex
cd /opt/trex

[ ! -f /opt/trex/v2.87.tar.gz ] && wget --no-cache https://trex-tgn.cisco.com/trex/release/v2.87.tar.gz
[ ! -d /opt/trex/v2.87 ] && tar -xzvf v2.87

python3.6 -m pip install lbr-trex-client --extra-index-url https://trex_client_deploy_token:vyd-dNs7ZnqpUfkm4o-v@gitlab.liberouter.org/api/v4/projects/79/packages/pypi/simple

cd v2.87
res=$(sudo ./trex_daemon_server show)
if [[ "$res" == "TRex server daemon is NOT running" ]]; then
    sudo ./trex_daemon_server start
fi

cd $mypwd
python3.6 "$1" "$2" # 1. path to the file with packets generator, 2. path to the output file with statistics
