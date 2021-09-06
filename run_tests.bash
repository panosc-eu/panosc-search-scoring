#!/bin/bash
#
#

# env variable do not work
#PSS_MONGODB_URL="mongodb://127.0.0.1:27017" PSS_DATABASE="pss" PSS_PORT="8000" 

# copy config to correct place
cp test/test_config_file.json config/pss_config.json

python -m pytest

rm config/pss_config.json




