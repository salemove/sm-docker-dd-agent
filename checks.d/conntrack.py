"""
Linux conntrack metrics (AWS Instance)

User must must be root or have CAP_NET_ADMIN capability to use this. In
kubernetes, the capability can be given to the container by specifying the
following securityContext for it.

```
securityContext:
  capabilities:
    add: ["NET_ADMIN"]
```
"""

import re
from datadog_checks.base.checks import AgentCheck
from datadog_checks.base.utils.subprocess_output import get_subprocess_output


class Conntrack(AgentCheck):
    def check(self, instance):
        for name, value, tags in self._get_conntrack_metrics():
            metric_key = "system.net.nf.conntrack_%s" % (name)
            self.gauge(metric_key, value, tags)

    def _get_conntrack_metrics(self):
        sysctl, err, retcode = get_subprocess_output([
            'cat',
            '/proc/sys/net/netfilter/nf_conntrack_count',
            '/proc/sys/net/netfilter/nf_conntrack_max'
        ], self.log, raise_on_empty_output=True)
        sysctl_lines = sysctl.split('\n')
        sysctl_results = [('count', sysctl_lines[0], []),
                          ('max', sysctl_lines[1], [])]

        conntrack, err, retcode = get_subprocess_output([
            'conntrack', '-S'
        ], self.log, raise_on_empty_output=True)
        # Sample output:
        # cpu=0           found=0 invalid=7796 ignore=16110 insert=0 insert_failed=0 drop=0 early_drop=0 error=0 search_restart=671
        # cpu=1           found=0 invalid=7234 ignore=15503 insert=0 insert_failed=0 drop=0 early_drop=0 error=0 search_restart=575
        # cpu=2           found=0 invalid=6589 ignore=16296 insert=0 insert_failed=0 drop=0 early_drop=0 error=0 search_restart=596
        # cpu=3           found=387 invalid=80384 ignore=17594 insert=0 insert_failed=0 drop=0 early_drop=0 error=0 search_restart=3923
        line_regex = re.compile(r'^\s*cpu=(\d)+\s+([\w=\s]+)$')
        param_regex = re.compile(r'(\w+)=(\d+)')

        try:
            return sysctl_results + [(name, value, tags)
                                     for line in conntrack.split('\n')
                                     for match in [re.match(line_regex, line)] if match
                                     for cpu, params in [match.groups()]
                                     for tags in ['cpu:'+cpu]
                                     for name, value in re.findall(param_regex, params)]
        except Exception:
            self.log.exception("Cannot parse %s" % (conntrack))
            return sysctl_results

