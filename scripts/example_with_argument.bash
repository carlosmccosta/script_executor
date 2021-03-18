#!/usr/bin/env bash

trap 'exit 1' ERR

argument=${1:-"7"}

echo "Example script with argument:" ${argument}
