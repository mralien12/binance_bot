#!/bin/sh

# List of coinpair
	# BTCUSDT \
	# 1INCHUSDT \
	# DOGEUSDT \
	# EGLDUSDT \
	# SFPUSDT \
	# ALPHAUSDT \
	# CAKEUSDT \

#

mkdir -p __binance_cache__

SLEEP_TIME=1 #seconds
history_interval=1h
coin_pair="
	SFPUSDT \
	"


help() {
	echo "Binance Bot"
	echo "Build date: Sat 03 Apr 2021 08:35:34 AM +07"	
	echo
	echo "Usage:"
	echo " $(basename $0) [options] <history_interval>"
	echo
	echo "Options:"
	echo " -i <history_interval>		history interval"
	echo "    invalid history interval - 1m, 3m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M"
	echo
	echo "Example:"
	echo " $(basename $0) -i 15m"

	exit
}

do_check_rsi() {
	for coin in $coin_pair;
	do
		rc=`ps -ef | grep buy | grep $coin`
		if [ -z "$rc" ]; then
			python3 buy_based_on_rsi.py $coin $history_interval &
			sleep $SLEEP_TIME
		fi
		# rc=`ps -ef | grep sell | grep $coin`
		# if [ -z "$rc" ]; then
		# 	python3 sell_based_on_rsi.py $coin $history_interval &
		# 	sleep $SLEEP_TIME
		# fi
	done
}

if [ $# -lt 2 ]; then
	help
fi

history_interval=$2
### Forever loop
while true
do
	do_check_rsi
	sleep 300
done

exit
