# iptables_xt_recent_parser
Used for converting jiffies from iptables xt_recent into timestamps.

An example of xt_recent log can be like this, where only 2 syn connections in 20 seconds are allowed:

````
export IPT=iptables
export SSH_PORT=22
export HITCOUNT=3 # 2 syn connection (<3)
export SECONDS=20 # in 20 seconds are allowed


# --rcheck: Check if the source address of the packet is  currently  in  the list.
# --update: Like  --rcheck,  except it will update the "last seen" timestamp if it matches.

$IPT -A INPUT -p tcp -m tcp --dport $SSH_PORT -m state --state NEW -m recent --set --name sshguys --rsource
$IPT -A INPUT -p tcp -m tcp --dport $SSH_PORT -m state  --state NEW  -m recent --rcheck --seconds $SECONDS --hitcount $HITCOUNT --rttl --name sshguys --rsource -j LOG --log-prefix "BLOCKED SSH (brute force)" --log-level 4 -m limit --limit 1/minute --limit-burst 5
$IPT -A INPUT -p tcp -m tcp --dport $SSH_PORT -m recent --rcheck --seconds $SECONDS --hitcount $HITCOUNT --rttl --name sshguys --rsource -j REJECT --reject-with tcp-reset
$IPT -A INPUT -p tcp -m tcp --dport $SSH_PORT -m recent --update --seconds $SECONDS --hitcount $HITCOUNT --rttl --name sshguys --rsource -j REJECT --reject-with tcp-reset
$IPT -A INPUT -p tcp -m tcp --dport $SSH_PORT -m state --state NEW,ESTABLISHED  -j ACCEPT
````

In syslog we can see blocked connections :

````
Mar 26 14:06:41 cloudone-cla kernel: [5339977.637052] BLOCKED SSH (brute force)IN=eth0 OUT= MAC=00:50:56:92:00:04:00:14:c2:61:09:be:08:00 SRC=95.142.177.153 DST=160.97.104.18 LEN=60 TOS=0x00 PREC=0x00 TTL=50 ID=42489 DF PROTO=TCP SPT=44636 DPT=22 WINDOW=29200 RES=0x00 SYN URGP=0
````

### Usage
````
XT_RECENT python parser
<giuseppe.demarco@unical.it>

usage: ipt_recents [-h] [-f F] [-txt] [-csv]

optional arguments:
  -h, --help  show this help message and exit
  -f F        custom xt_recent path, default if omitted is:
              /proc/net/xt_recent/DEFAULT
  -txt        print it in human readable format
  -csv        print it in CSV format
````

### Output
````
Standard readable view:
190.102.72.44, last seen: 2017-03-26 13:31:55 after 1 connections
187.112.185.153, last seen: 2017-03-26 13:28:07 after 2 connections
95.142.177.153, last seen: 2017-03-26 13:27:31 after 12 connections

CSV view:
ip_src;last_seen;connections;deltas_mean;delta_seconds
190.102.72.44;2017-03-26 13:31:55.462201;1;0;
187.112.185.153;2017-03-26 13:28:07.168819;2;0.0;0
95.142.177.153;2017-03-26 13:27:31.976049;12;1.7272727272727273;1,1,1,1,1,1,2,3,3,1,4

````

In CSV format there are time delta mean and time delta in seconds, for every attempts.

### Requirements

- Python3
