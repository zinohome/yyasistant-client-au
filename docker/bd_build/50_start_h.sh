#!/bin/bash
cd /opt/yyasistant-client && \
. venv/bin/activate && \
nohup /opt/yyasistant-client/venv/bin/chainlit run app.py -h --host 0.0.0.0 --port 8000 >> /tmp/yyasistant-client.log 2>&1 &