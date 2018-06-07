"""
Linux conntrack metrics (AWS NAT Instance)
"""

import subprocess as sp
import re
from checks import AgentCheck


class Conntrack(AgentCheck):

    def check(self, instance):
        conntrack_info = self._get_sysctl_metrics()
        for metric, value in conntrack_info.iteritems():
            metric_key = "system.net.nf.%s" % (metric)
            self.gauge(metric_key, value)

    def _get_sysctl_metrics(self):
        sysctl = sp.Popen(['cat', '/proc/sys/net/netfilter/nf_conntrack_count',
                           '/proc/sys/net/netfilter/nf_conntrack_max'],
                          stdout=sp.PIPE, close_fds=True).communicate()[0]
        lines = sysctl.split('\n')
        conntrack_info = {}
        conntrack_info['conntrack_count'] = lines[0]
        conntrack_info['conntrack_max'] = lines[1]
        return conntrack_info
