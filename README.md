# xt_recent_parser
Tool used for converting jiffies from iptables xt_recent timestamps.
These timestamps were produced by iptables recent logging action.

An example of ssh recent recent activity could be as this:

````
export IPT=iptables
export SSH_PORT=22

$IPT -A INPUT -p tcp --dport $SSH_PORT -m state --state NEW -m recent --name sshguys  --rcheck --seconds 60 --hitcount 13 -j LOG --log-prefix "BLOCKED SSH CONNECTION " --log-level 4 -m limit --limit 1/minute --limit-burst 5
# --update: Like  --rcheck,  except it will update the "last seen" timestamp if it matches.
$IPT -A INPUT -p tcp --dport $SSH_PORT -m state --state NEW -m recent --name sshguys  --update --seconds 60 --hitcount 13 -j DROP
$IPT -A INPUT -p tcp --dport $SSH_PORT -m state --state NEW,ESTABLISHED -m recent --name sshguys --set -j ACCEPT
````

It only needs Python3:

python3 xt_recent_parser.py
