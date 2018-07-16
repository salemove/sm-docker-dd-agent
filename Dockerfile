FROM datadog/docker-dd-agent:12.6.5250

# Add some new features and fixes from upsteam
# Not very elegant, but it is easier than creating custom deb package

ADD conf.d/ /etc/dd-agent/conf.d/
ADD checks.d/ /etc/dd-agent/checks.d/

# Apply patches
ADD patches/*.patch /tmp/
RUN apt-get update \
 && apt-get install --no-install-recommends -y patch netbase \
 && (for p in `ls /tmp/*.patch`; do echo "Applying: $p"; patch -p1 < $p || exit 1; done) \
 && apt-get remove -y --force-yes patch \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# required for reporting conntrack_insert_failed and conntrack_drop metrics
RUN apt-get update && apt-get install -y --no-install-recommends conntrack

COPY entrypoint-wrapper.sh /entrypoint-wrapper.sh

ENTRYPOINT ["/entrypoint-wrapper.sh"]
# Overriding entrypoint resets CMD, so we have to include it here
# https://github.com/docker/docker/issues/5147
CMD ["supervisord", "-n", "-c", "/etc/dd-agent/supervisor.conf"]
