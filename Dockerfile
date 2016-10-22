FROM datadog/docker-dd-agent:11.0.591

ADD conf.d/ /etc/dd-agent/conf.d/
ADD checks.d/ /etc/dd-agent/checks.d/

COPY entrypoint-wrapper.sh /entrypoint-wrapper.sh

ENTRYPOINT ["/entrypoint-wrapper.sh"]
# Overriding entrypoint resets CMD, so we have to include it here
# https://github.com/docker/docker/issues/5147
CMD ["supervisord", "-n", "-c", "/etc/dd-agent/supervisor.conf"]
