#!/bin/bash
#set -e

if [[ $RABBITMQ_USER ]]; then
    sed -i -e "s/rabbitmq_user:.*$/rabbitmq_user: ${RABBITMQ_USER}/" /etc/dd-agent/conf.d/auto_conf/rabbitmq.yaml
fi

if [[ $RABBITMQ_PASS ]]; then
    sed -i -e "s/rabbitmq_pass:.*$/rabbitmq_pass: ${RABBITMQ_PASS}/" /etc/dd-agent/conf.d/auto_conf/rabbitmq.yaml
fi

exec /entrypoint.sh "$@"
