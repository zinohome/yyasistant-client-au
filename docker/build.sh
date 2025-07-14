#!/bin/bash
IMGNAME=zinohome/yyassistant-client
IMGVERSION=v0.0.1
docker build --no-cache -t $IMGNAME:$IMGVERSION .