#!/usr/bin/env bash

trap 'exit 1' ERR

argument_1=${1:-"A"}
argument_2=${2:-"7"}

echo "Example script with argument 1:" ${argument_1} "and argument 2:" ${argument_2}
