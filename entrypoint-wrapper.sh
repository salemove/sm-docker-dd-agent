#!/bin/bash
#set -e

if [[ $RABBITMQ_USER ]]; then
    sed -i -e "s/rabbitmq_user:.*$/rabbitmq_user: ${RABBITMQ_USER}/" /etc/dd-agent/conf.d/auto_conf/rabbitmq.yaml
fi

if [[ $RABBITMQ_PASS ]]; then
    sed -i -e "s/rabbitmq_pass:.*$/rabbitmq_pass: ${RABBITMQ_PASS}/" /etc/dd-agent/conf.d/auto_conf/rabbitmq.yaml
fi

# Make sure histograms are disabled, so far they have been disabled in kubernetes
# Also they are disabled in master but not in last release
sed -rie 's/^(\s+)\suse_histogram:/\1# use_histogram:/' /etc/dd-agent/conf.d/kubernetes.yaml.example

exec /entrypoint.sh "$@"
