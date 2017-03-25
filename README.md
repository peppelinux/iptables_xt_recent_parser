# xt_recent_parser
Tool used for converting jiffies from iptables xt_recent timestamps.
These timestamps were produced by iptables recent logging action.

An example of ssh recent recent activity could be as this:

````
export IPT=iptables
export SSH_PORT=22

# --rcheck: Check if the source address of the packet is  currently  in  the list.
$IPT -A TCP_SERVICES -p tcp --dport $SSH_PORT -m state --state NEW -m recent --name sshguys  --rcheck --seconds 60 --hitcount 27 -j LOG --log-prefix "BLOCKED SSH CONNECTION " --log-level 4 -m limit --limit 1/minute --limit-burst 5
# --update: Like  --rcheck,  except it will update the "last seen" timestamp if it matches.
$IPT -A TCP_SERVICES -p tcp --dport $SSH_PORT -m state --state NEW -m recent --name sshguys  --update --seconds 60 --hitcount 27 -j DROP
$IPT -A TCP_SERVICES -p tcp --dport $SSH_PORT -m state --state NEW,ESTABLISHED -m recent --name sshguys --set -j ACCEPT
````

It only needs Python3:

````
root@cloudone-cla:~/xt_recent_parser# python3 xt_recent_parser.py 
XT_RECENT python parser
<giuseppe.demarco@unical.it>


114.241.108.160, last seen: 2017-03-25 18:21:42 after 13 Connections 
46.165.210.17, last seen: 2017-03-25 13:07:54 after 10 Connections 
61.53.219.162, last seen: 2017-03-25 17:39:17 after 20 Connections 
179.37.141.232, last seen: 2017-03-25 18:08:23 after 2 Connections 
114.42.117.39, last seen: 2017-03-25 13:22:14 after 18 Connections 
177.12.84.234, last seen: 2017-03-25 16:22:14 after 17 Connections 

````

Mind to edit the xt_recent file path first:

````
xt = XtRecentTable(fpath="/proc/net/xt_recent/sshguys")
````
