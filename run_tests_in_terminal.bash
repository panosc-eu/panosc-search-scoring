#!/bin/bash

clear
export PSS_MONGODB_URL="mongodb://127.0.0.1:27017"
export PSS_DATABASE="pss_test"
export PSS_PORT="8000"
export PSS_VERSION="vTest"

python -m pytest test



