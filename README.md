# DataDog Agent Dockerfile with additional checks

This is a wrapper image around official DataDog Agent Dockerfile to add configuration templates for DataDog Service Discovery.
There are 3 ways to define configuration templates for DataDog Service Discovery, in etcd, Consul or locally in `/etc/dd-agent/conf.d/auto_conf/`.
If you do not want to manage etcd or Consul then you have to add template files to docker image.

`entrypoint-wrapper.sh` is used to replace variables/parameters in config files. E.g you can use env variables to specify username and password for RabbitMQ.
