FROM phusion/passenger-full:latest
MAINTAINER zhangjun <ibmzhangjun@139.com>

COPY bd_build/* /bd_build/
# Sys ENV
ENV DEBIAN_FRONTEND noninteractive
ENV HOME /root
ENV EXT_HOSTS=''

# ...put your own build instructions here...
RUN mkdir -p /data && chmod 755 /bd_build/install.sh && /bd_build/install.sh

# Clean up APT when done.
WORKDIR /opt/yyasistant-client-au/

# Use baseimage-docker's init system.
EXPOSE 8000
VOLUME ["/data"]
CMD ["/sbin/my_init"]