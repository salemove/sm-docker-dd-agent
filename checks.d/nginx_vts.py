# (C) SaleMove, Inc. 2016
# (C) Datadog, Inc. 2010-2016
# All rights reserved
# Licensed under Simplified BSD License (see LICENSE)

# stdlib
import re
from urllib.parse import urlparse

# 3rd party
import requests
import simplejson as json

# project
from datadog_checks.base.utils.headers import headers
from datadog_checks.base.checks import AgentCheck

METRIC_TYPES = {
    'responseMsec': 'gauge',
    'requestMsec':  'gauge',
    'weight':       'gauge',
    'maxFails':     'gauge',
    'failTimeout':  'gauge',
    'backup':       'gauge',
    'down':         'gauge',
    'loadMsec':     'gauge',
    'nowMsec':      'gauge',
    'maxSize':      'gauge',
    'usedSize':     'gauge'
}

def lreplace(s, old, new):
    return re.sub(r'^(?:%s)+' % re.escape(old), lambda m: new * (m.end() / len(old)), s)

class NginxVts(AgentCheck):
    """Tracks nginx metrics via virtual host traffic status module

    See https://github.com/vozlt/nginx-module-vts

    $ curl http://localhost:80/nginx_vts/


    """
    def check(self, instance):
        if 'nginx_vts_url' not in instance:
            raise Exception('Nginx vts instance missing "nginx_vts_url" value.')
        tags = instance.get('tags', [])

        response, content_type = self._get_data(instance)
        self.log.debug(u"Nginx status `response`: {0}".format(response))
        self.log.debug(u"Nginx status `content_type`: {0}".format(content_type))

        metrics = self.parse_json(response, tags)

        funcs = {
            'gauge': self.gauge,
            'rate': self.rate
        }
        for row in metrics:
            try:
                name, value, tags, metric_type = row
                func = funcs[metric_type]
                func(name, value, tags)
            except Exception as e:
                self.log.error(u'Could not submit metric: %s: %s' % (repr(row), str(e)))

    def _get_data(self, instance):
        url = instance.get('nginx_vts_url')
        ssl_validation = instance.get('ssl_validation', True)

        auth = None
        if 'user' in instance and 'password' in instance:
            auth = (instance['user'], instance['password'])

        # Submit a service check for status page availability.
        parsed_url = urlparse(url)
        nginx_host = parsed_url.hostname
        nginx_port = parsed_url.port or 80
        service_check_name = 'nginx_vts.can_connect'
        service_check_tags = ['host:%s' % nginx_host, 'port:%s' % nginx_port]
        try:
            self.log.debug(u"Querying URL: {0}".format(url))
            r = requests.get(url, auth=auth, headers=headers(self.agentConfig),
                             verify=ssl_validation)
            r.raise_for_status()
        except Exception:
            self.service_check(service_check_name, AgentCheck.CRITICAL,
                               tags=service_check_tags)
            raise
        else:
            self.service_check(service_check_name, AgentCheck.OK,
                               tags=service_check_tags)

        body = r.content
        resp_headers = r.headers
        return body, resp_headers.get('content-type', 'text/plain')

    @classmethod
    def parse_json(cls, raw, tags=None):
        if tags is None:
            tags = []
        parsed = json.loads(raw)
        metric_base = 'nginx_vts'
        output = []
        all_keys = parsed.keys()

        tagged_keys = ['cacheZones', 'serverZones', 'upstreamZones', 'filterZones']

        # Process the special keys that should turn into tags instead of
        # getting concatenated to the metric name
        for key in tagged_keys:
            metric_name = '%s.%s' % (metric_base, key)
            for tag_val, data in parsed.get(key, {}).iteritems():

                # skip total values
                if tag_val != '*':
                    tag = '%s:%s' % (key, lreplace(tag_val,':','_'))
                    output.extend(cls._flatten_json(metric_name, data, tags + [tag]))

        # Process the rest of the keys
        rest = set(all_keys) - set([k for k in tagged_keys])
        for key in rest:
            metric_name = '%s.%s' % (metric_base, key)
            output.extend(cls._flatten_json(metric_name, parsed[key], tags))

        return output

    @classmethod
    def _flatten_json(cls, metric_base, val, tags):
        """ Recursively flattens the nginx json object. Returns the following:
            [(metric_name, value, tags)]
        """
        output = []
        if isinstance(val, dict):
            # Pull out the server as a tag instead of trying to read as a metric
            if 'server' in val and val['server']:
                server = 'server:%s' % val.pop('server')
                if tags is None:
                    tags = [server]
                else:
                    tags = tags + [server]
            for key, val2 in val.iteritems():
                # Skip requestMsecs and responseMsecs, no good way to show them in DataDog
                if key in ['requestMsecs', 'responseMsecs']:
                    continue

                if key != 'overCounts':

                    # Handle overcounts
                    if key in ['requestCounter', 'inBytes', 'outBytes']:
                        val2 = val2 + int(val['overCounts']['maxIntegerSize']) * val['overCounts'][key]
                    if key == 'responses':
                        for key_resp, val_resp in val2.iteritems():
                            val[key][key_resp] = val_resp + int(val['overCounts']['maxIntegerSize']) * val['overCounts'][key_resp]

                    metric_name = '%s.%s' % (metric_base, key)
                    output.extend(cls._flatten_json(metric_name, val2, tags))

        elif isinstance(val, list):
            for val2 in val:
                output.extend(cls._flatten_json(metric_base, val2, tags))

        elif isinstance(val, bool):
            # Turn bools into 0/1 values
            if val:
                val = 1
            else:
                val = 0
            output.append((metric_base, val, tags, METRIC_TYPES.get(metric_base.split('.')[-1], 'rate')))

        elif isinstance(val, (int, float)):
            output.append((metric_base, val, tags, METRIC_TYPES.get(metric_base.split('.')[-1], 'rate')))

        return output
