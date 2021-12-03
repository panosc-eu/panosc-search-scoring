#!/bin/bash
#
#
clear

PSS_DEBUG=1 PSS_MONGODB_URL="mongodb://127.0.0.1:27017" PSS_DATABASE="pss_test" PSS_PORT="8000" PSS_DEPLOYMENT="pss-local-test" python main.py

