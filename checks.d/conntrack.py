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
        sysctl_lines = sysctl.split('\n')
        conntrack_info = {}
        conntrack_info['conntrack_count'] = sysctl_lines[0]
        conntrack_info['conntrack_max'] = sysctl_lines[1]

        conntrack = sp.Popen(['conntrack', '-S'],
                          stdout=sp.PIPE, close_fds=True).communicate()[0]
        # Sample output:
        # entries   		8112
        # searched  		0
        # found     		72556
        # new       		0
        # invalid   		3828562
        # ignore    		13996314
        # delete    		0
        # delete_list		0
        # insert    		0
        # insert_failed		12783
        # drop      		12783
        # early_drop		0
        # icmp_error		1
        # expect_new		0
        # expect_create		0
        # expect_delete		0
        # search_restart		32917695
        conntrack_lines = conntrack.split('\n')
        regexp = re.compile(r'^(\w+)\s+([0-9]+)')
        for line in conntrack_lines:
            try:
                match = re.search(regexp, line)
                if match is not None:
                    conntrack_info['conntrack_{}'.format(match.group(1))] = match.group(2)
            except Exception:
                self.log.exception("Cannot parse %s" % (line,))
        return conntrack_info
