FROM datadog/agent:7.27.0@sha256:f9ff7b837260dea225045b7d27946ea7b984f43b79d7783b568910f69aa2a7b4

# Required for reporting conntrack_insert_failed and conntrack_drop metrics
RUN apt-get update && apt-get install -y --no-install-recommends conntrack \
 && rm -rf /var/lib/apt/lists/*

ADD checks.d/ /checks.d
