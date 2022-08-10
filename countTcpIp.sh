#!/bin/bash

function compare_str {
    local tmp=0
    local line=$2
    local proto=$1
    
    local proto_rule=$(echo "$line" | awk -F' ' '{print $2}')
    
    for i in "${@:3}"
    do
        if [[ "$line" == *" $i"* ]] && [[ "$proto" == "$proto_rule" ]]; then
            echo -e "pattern: $i \n $line"
            ((tmp=tmp+1))
        fi
    done

    return $tmp
}

declare -a tcp_kwds=(" ack:" " seq:" " window:" " tcp.mss:" " tcp.hdr:")
declare -a ip_kwds=(" ttl:" " ipopts:" " sameip:" " ip_proto:" " ipv4.hdr:" " ipv6.hdr:" " id:" " geoip:" " fragbits:" " fragoffset:" " tos:")
tcp=0
ip=0

while read -r line
do
	if [ "${line:0:1}" == "#" ] || [ "${line:0:1}" == "\n" ]; then
		continue
	fi
    
    compare_str "tcp" "$line" ${tcp_kwds[@]}
    ((tcp=tcp+$?)
    compare_str "ip" "$line" ${ip_kwds[@]}
    ((ip=ip+$?))
done < $1

echo "ip: $ip"
echo "tcp: $tcp"
