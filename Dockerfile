FROM datadog/agent:7.22.1

# Required for reporting conntrack_insert_failed and conntrack_drop metrics
RUN apt-get update && apt-get install -y --no-install-recommends conntrack \
 && rm -rf /var/lib/apt/lists/*

ADD checks.d/ /checks.d
ADD datadog_checks/ /datadog_checks

RUN cp -r /datadog_checks/* /opt/datadog-agent/embedded/lib/python3.8/site-packages/datadog_checks/
