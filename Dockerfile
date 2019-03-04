FROM datadog/agent:6.10.0

# Required for reporting conntrack_insert_failed and conntrack_drop metrics
RUN apt-get update && apt-get install -y --no-install-recommends conntrack \
 && rm -rf /var/lib/apt/lists/*

ADD checks.d/ /checks.d
