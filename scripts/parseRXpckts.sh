#!/bin/bash
AUTOR="Flavio Meneses @ University of Aveiro, 2015"
USAGE="Usage: `basename $0` -h | help"
# default values
IFACE="eth0"
T="10"

if [[ "$1" == "-h" ]]; then
  echo "$USAGE"
  echo "AUTOR: $AUTOR"
  echo ""
  echo "[-h ]                    help"
  echo "[-i | --interface]       select interface"
  echo "[-t | --timeinterval]    choose the time interval through the array index"
  echo "                         [0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1 2 3 4 5]"
  exit

elif [[ "$1" == "--default" ]]; then
	echo "DEFAULT inputs: -i $IFACE -t $T"

else
  if [[ $# < 2 ]]; then
  	echo "Invalid argument [$1]"
  	echo "$USAGE"
	exit
  fi
  while [[ $# > 1 ]]
  do
    key="$1"
    case $key in
      -i|--interface)
        IFACE="$2"
        shift
        ;;
      -t|--timeinterval)
        if [[ "$2" -lt 15 ]] && [[ "$2" -ge 1 ]]; then
          T="$2"
        else
      	  echo "Array index too high! (value between [1-14])"
          exit
        fi
        shift
        ;;
      *)
        echo "Invalid argument [$1 $2]"
        echo "$USAGE"
        exit
        ;;
    esac
    shift
  done
fi

TIME_INTERVAL=(0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1 2 3 4 5)

# will be divided by 10 
TIME_INTERVAL_BITRATE=(1 2 3 4 5 6 7 8 9 8 20 30 40 50)
HANDOVER_TOLERANCE=0.5
# variables 
CRX=0
MAX_CRX=3
CT=0
MAX_CT=3
FLAG=false
# 54 Mbps = 6.75 MBps = 6912 KBps
#MAX_LOAD=6912
MAX_LOAD=$((20 * 1024 * 1024))
PERCENT=90
TRIGGER_LOAD=$((PERCENT * MAX_LOAD / 100))

echo Interface: "$IFACE"
echo Interval Time: "${TIME_INTERVAL[$T-1]}"
echo Trigger Load: "$TRIGGER_LOAD"

while true; do
  # read interface received bytes
  read RX_PCKTS_OLD <<< $(ifconfig $IFACE | grep 'RX bytes'| awk '{ print $2}' | grep -o [0-9] | tr -d '\n')
  sleep ${TIME_INTERVAL[$T-1]}
  # read interface received bytes afteer an interval time
  read RX_PCKTS <<< $(ifconfig $IFACE | grep 'RX bytes'| awk '{ print $2}' | grep -o [0-9] | tr -d '\n')
  
  # calc the interface bitrate and save it in the buffer 
  # the multiplication and division by 10 is due to the fact the bash cannot calc float numbers
  RX_PCKTS_OLD=$(RX_PCKTS_OLD * 8)
  RX_PCKTS=$(RX_PCKTS * 8)
  RX_BITRATE_VALUES[$CRX]=$(((RX_PCKTS - RX_PCKTS_OLD) * 10 / TIME_INTERVAL_BITRATE[T-1]))
  #RX_BITRATE_VALUES[$CRX]=$(((RX_PCKTS - RX_PCKTS_OLD) * 10 / TIME_INTERVAL_BITRATE[T-1] / 1024 / 1024))
  #echo buffer: "${RX_BITRATE_VALUES[*]}"
  
  # create a circular buffer
  CRX=$((CRX+1))
  if [[ CRX -eq MAX_CRX ]]; then
    # buffer full
    CRX=0
    # active flag to allow the average calc
    if [[ "$FLAG" = false ]]; then
      #echo "flag"
      FLAG=true
    fi
  fi

  # if buffer is already full calc bitrate average
  if [[ "$FLAG" = true ]]; then
	  # calc array average
	  BITRATE_AVG=0
	  for (( i = 0; i < $MAX_CRX; i++ )); do
	    BITRATE_AVG=$((BITRATE_AVG + RX_BITRATE_VALUES[i]))	
	  done
	  echo "$BITRATE_AVG"
	  BITRATE_AVG=$((BITRATE_AVG / MAX_CRX))
      #BITRATE_AVG_M=$((BITRATE_AVG / 1024 / 1024))

      echo bitrate: "$BITRATE_AVG" bps
      #echo bitrate: "$BITRATE_AVG_M" Mbps

	  if [[ BITRATE_AVG -ge TRIGGER_LOAD ]]; then
      #flag trigger count ++
      CT=$((CT+1))
      echo "bitrate: $BITRATE_AVG Mbps"
      echo "Trigger Counter: $CT"
      if [[ CT -eq MAX_CT ]]; then
      	# send trigger to controller
      	echo “help” > /dev/udp/33.33.33.33/58549
        echo "TRIGGER SENT!"
        CT=0
        if [[ ${TIME_INTERVAL[$T-1]} < $HANDOVER_TOLERANCE ]]; then
          #echo "WAIT FOR HANDOVER"
          sleep $HANDOVER_TOLERANCE
        fi

      fi
	  else
	    #flag trigger count=0
	    CT=0
	  fi
  fi

done