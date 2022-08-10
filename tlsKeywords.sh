#!/bin/bash

RED='\033[0;31m'
NC='\033[0m'
BLUE='\033[0;34m'

declare -a metadata_kwds=("msg" "sid" "rev" "gid" "classtype" "reference" "priority" "metadata" "target"
                          "content" "nocase" "depth" "startswith" "endswith" "offset" "distance" "within"
                          "isdataat" "bsize" "dsize" "byte_test" "byte_math" "byte_jump" "byte_extract" "rpc" "replace" "pcre")
cat $1 | awk -F' ' '$2 == "tls" {printf "%s\\n\n",$0}' > tls_traffic.txt

declare -a final=()

while read -r line; do
    delimiter="; "
    s=$line$delimiter  
    array=()
    while [[ $s ]]; do
        array+=( "${s%%"$delimiter"*}" )
        s=${s#*"$delimiter"}
    done

    for i in "${array[@]:1}"; do
        flag=0
        kwd=$(echo $i | awk -F':' '{print $1}')
        
        for m_kwd in "${metadata_kwds[@]}"; do
            if [[ "$kwd" == "$m_kwd" ]]; then
                flag=1
            fi
        done

        if [ "$flag" -eq "0" ]; then
            final+=("$kwd")
        fi
    done
done < tls_traffic.txt

rm tls_traffic.txt
echo "${final[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' '
echo
