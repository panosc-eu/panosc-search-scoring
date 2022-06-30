#!/bin/bash

clear
docker-compose -f docker/docker-compose_unittest.yml up -d
RET_CODE=$(docker wait panosc-search-scoring-unittest)
docker logs panosc-search-scoring-unittest
docker-compose -f docker/docker-compose_unittest.yml down
exit $RET_CODE
