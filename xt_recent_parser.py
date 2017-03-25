#~ Copyright 2017 Giuseppe De Marco <giuseppe.demarco@unical.it>
#~ 
#~ Permission is hereby granted, free of charge, to any person obtaining a 
#~ copy of this software and associated documentation files (the "Software"), 
#~ to deal in the Software without restriction, including without limitation 
#~ the rights to use, copy, modify, merge, publish, distribute, sublicense, 
#~ and/or sell copies of the Software, and to permit persons to whom the Software 
#~ is furnished to do so, subject to the following conditions:
#~ 
#~ The above copyright notice and this permission notice shall be included 
#~ in all copies or substantial portions of the Software.
#~ 
#~ THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS 
#~ OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
#~ FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
#~ THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
#~ LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
#~ FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
#~ DEALINGS IN THE SOFTWARE.

import re
import sys
import datetime
from copy import copy
import os
import subprocess

_debug = False
_fpath = '/proc/net/xt_recent/DEFAULT'

_src_pattern = r'(?:src\=)(?P<src>[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})'
_ttl_pattern = r'(?:ttl\:\ )(?P<ttl>[0-9]+)'
_last_seen_pattern = r'(?:last_seen\:\ )(?P<last_seen>[0-9]+)'
_hitcount_pattern = r'(?:hitcount\:\ )(?P<hitcount>[0-9]+)'
_oldest_pkt_pattern = r'(?:oldest_pkt\:\ )(?P<oldest_pkt>[0-9]+)'
_timestamps_pattern = r'(?:oldest_pkt\:\ [0-9]*)(?P<timestamps>[0-9 ,]+)'


_kernel_config_path = '/boot/config-'+subprocess.getoutput(['uname -r'])

def check_system_jiffies():
    last_jiffies = 0
    hz = 0
    cnt = 0
    while cnt < 33:
        new_jiffies = system_jiffies()
        hz = new_jiffies - last_jiffies
        last_jiffies = new_jiffies
        time.sleep(1)
        print(hz)
        print(new_jiffies)
        print('')
        cnt += 1
    return hz

def system_uptime():
    from datetime import timedelta
    
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        uptime_string = str(timedelta(seconds = uptime_seconds))
    
    print(uptime_string)
    return uptime_seconds

def system_jiffies():
    _jiffies_pattern = r'(?:jiffies[ =:]*?)([0-9]+)'
    
    with open('/proc/timer_list') as f:
        q = re.search(_jiffies_pattern, f.read())
        if not q:
             sys.exit('Cannot determine jiffies in /proc/timer_list.\n\
    Please check _jiffies_pattern\n\n')
        else:
            _jiffies = q.groups()[0]
    return float(_jiffies)

def system_btime():
    """
    The "btime" line gives the time at which the system booted, in seconds since
    the Unix epoch.
    """
    _pattern = r'(?:btime[ =:]*?)([0-9]+)'
    
    with open('/proc/stat') as f:
        q = re.search(_pattern, f.read())
        if not q:
             sys.exit('Cannot determine btime in /proc/stat.\n\
    Please check _jiffies_pattern\n\n')
        else:
            _btime = q.groups()[0]
    return float(_btime)

def system_hz(kernel_config_path=_kernel_config_path):        
    # HZ defined how many ticks the internal timer interrupt in 
    # 1sec, which means the number of jiffies count in 1 sec.
    _HZ_pattern = r'(?:CONFIG_HZ[ =:]*?)([0-9]+)'
    
    with open(kernel_config_path) as f:
        q = re.search(_HZ_pattern, f.read())
        if not q:
             sys.exit('Cannot determine kernel HZ freq\n\n')
        else:
            _hz = q.groups()[0]
    return float(_hz)
    
    
class JiffyTimeConverter(object):
    def __init__(self, kernel_config_path=_kernel_config_path):
        
        self.hz = system_hz(kernel_config_path=_kernel_config_path)
        self.jiffies = system_jiffies()
        
    def seconds_ago(self, jiffies_timestamp):
        return ((system_jiffies() - int(jiffies_timestamp) ) / self.hz )
    
    def minutes_ago(self, jiffies_timestamp):
        return self.seconds_ago / 60 
    
    def datetime(self, jiffies_timestamp):
        now = datetime.datetime.now()
        td = datetime.timedelta(seconds=self.seconds_ago(jiffies_timestamp))
        return now - td
    
    def convert_to_format(self, jiffy_timestamp, strftime='%Y-%m-%d %H:%M:%S'):
        return self.datetime(jiffy_timestamp).strftime(strftime)
        

class XtRecentRow(object):
    def __init__(self, row, debug=False):
        """
            where row is:
            src=151.54.175.212 ttl: 49 last_seen: 5610057758 
            oldest_pkt: 11 5610048214, 5610048235, 5610048281, [...]
        """
        
        d = {}
        d.update(re.search( _src_pattern, row ).groupdict())
        #~ self.hitcount   = d.update(re.search( _hitcount_pattern, row ).groupdict())
        d.update(re.search( _ttl_pattern, row ).groupdict())
        d.update(re.search( _last_seen_pattern, row ).groupdict())
        d.update(re.search( _oldest_pkt_pattern, row ).groupdict())
        
        for i in d:
            setattr(self, i, d[i])
        
        self.raw_history    = re.search( _timestamps_pattern, row ).groups()[0] #.replace(' ', '').split(',')
        self.history = [ i.strip() for i in self.raw_history.split(',')]
        
        if debug: 
            print(d)
            print(self.history)
            print('')
        
    def convert_jiffies(self, strftime_format='%Y-%m-%d %H:%M:%S'):
        d = copy(self)
        
        jt = JiffyTimeConverter()
        
        d.last_seen = jt.convert_to_format(d.last_seen, strftime_format)
        d.oldest_pkt = jt.convert_to_format(d.oldest_pkt, strftime_format)
        
        d.history = [ jt.convert_to_format(i, strftime_format) for i in self.history]
        return d
    
    def __repr__(self):
        return '%s, last seen: %s after %s Connections ' % ( self.src, self.last_seen, len(self.history))
        

class XtRecentTable(object):
    def __init__(self, fpath=None):
        if fpath:
            self.fpath = fpath
        else:
            self.fpath = _fpath
        
        self.xt_recent = []
        self.rows      = []
        
    def parse(self, debug=False):
        # flush it first
        self.rows = []
        with open(self.fpath) as f:
            self.rows = f.readlines()
        for i in self.rows:
            if i.strip():
                if debug:
                    print('Parsing: %s' % i.replace('\n', ''))
                row = XtRecentRow(i, debug=_debug)
                self.xt_recent.append( row )
                row_dt = row.convert_jiffies()
                print( row_dt)
                if debug:
                    for e in row_dt.history:
                        print(r)
                print('')
        
    
    def view(self):
        pass


if __name__ == '__main__':
    print('XT_RECENT python parser\n<giuseppe.demarco@unical.it>\n\n')
    xt = XtRecentTable(fpath='/proc/net/xt_recent/sshguys')
    xt.parse()

