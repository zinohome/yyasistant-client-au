#!/bin/bash
IMGNAME=zinohome/yyassistant-client-au
IMGVERSION=v0.0.2
docker build --no-cache -t $IMGNAME:$IMGVERSION .