FROM datadog/agent:7.25.1@sha256:538a3a9d8950ab90cfc37504a01908f8d03b65502836f66ecff2965c87d4e71e

# Required for reporting conntrack_insert_failed and conntrack_drop metrics
RUN apt-get update && apt-get install -y --no-install-recommends conntrack \
 && rm -rf /var/lib/apt/lists/*

ADD checks.d/ /checks.d
