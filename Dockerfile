FROM datadog/docker-dd-agent:11.0.5100

# Add some new features and fixes from upsteam
# Not very elegant, but it is easier than creating custom deb package
ADD opt/ /opt/

ADD conf.d/ /etc/dd-agent/conf.d/
ADD checks.d/ /etc/dd-agent/checks.d/

COPY entrypoint-wrapper.sh /entrypoint-wrapper.sh

ENTRYPOINT ["/entrypoint-wrapper.sh"]
# Overriding entrypoint resets CMD, so we have to include it here
# https://github.com/docker/docker/issues/5147
CMD ["supervisord", "-n", "-c", "/etc/dd-agent/supervisor.conf"]
