#!/bin/bash
cd /opt/yyasistant-client-au && \
. venv/bin/activate && \
nohup /opt/yyasistant-client-au/venv/bin/chainlit run app.py -h --host 0.0.0.0 --port 8000 >> /tmp/yyasistant-client-au.log 2>&1 &