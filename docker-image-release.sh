#!/usr/bin/env bash
#
# script filename
SCRIPT_NAME=$(basename $BASH_SOURCE)
echo ""
echo ""

#
# check that we got two arguments in input
if [ "$#" -ne 0 ] && [ "$#" -ne 1 ]; then
    echo "Usage ${SCRIPT_NAME} (<tag>)"
    echo ""
    echo " prepare a docker image and push it to the github container repository"
    echo " The image will be named:"
    echo "  - panosc-eu/panosc-search-scoring:<version>"
    echo "  - panosc-eu/panosc-search-scoring:stable"
    echo ""
    echo " This script requires the user to be logged in with their own account to github"
    echo " Users can log in by running the following command prior to running this script:"
    echo " > docker login ghcr.io --username <username>"
    echo ""
    echo " arguments:"
    echo " - tag     = git tag we would like to use to create the image"
    echo "             if not specified it uses the latest tag available on the main branch"
    echo ""
    exit 1
fi

gitTag=$1

# code repository and branch
# not used - TO BE DELETED
#gitRepo=https://github.com/panosc-eu/panosc-search-scoring.git
#branch=master

# package name
packageName="panosc-search-scoring"
# local container image
localContainerImage="panosc-eu/${packageName}:current"
# github container repositories
releaseContainerRepo="ghcr.io/panosc-eu/${packageName}"


# retrieve latest git commit tag
if [ "-${gitTag}-" == "--" ]; then 
    gitTag=$(git describe --tags --abbrev=0)
else
    # check out on the specific commit or tag
    git checkout ${gitTag}
fi


# docker image tag
releaseContainerTag="${gitTag}"
releaseContainerImage="${releaseContainerRepo}:${releaseContainerTag}"
stableContainerImage="${releaseContainerRepo}:stable"


#
# gives some feedback to the user
echo "Git commit tag           : ${gitTag}"
echo "Local Container image    : ${localContainerImage}"
echo "Release Container tag    : ${releaseContainerTag}"
echo "Release Container image  : ${releaseContainerImage}"
echo "Stable Container image   : ${stableContainerImage}"
echo ""

#
# create docker image
# if it is already present, remove old image
if [[ "$(docker images -q ${localContainerImage} 2> /dev/null)" != "" ]]; then
    echo "Image already present. Removing it and recreating it"
    docker rmi ${localContainerImage}
    echo ""
fi
echo "Creating conf file with version"
sed "s/<VERSION>/${dockerTag}/" docker/config_template.json > ./docker/pss_config.json
echo "Creating image"
docker build -t ${localContainerImage} -f ./docker/Dockerfile .
#echo "Removing config file"
##rm -f ./docker/config.json
#echo ""

echo "Tagging image for release ${releaseContainerImage}"
docker tag ${localContainerImage} ${releaseContainerImage}

# push image on docker hub repository
echo "Pushing release image"
docker push ${releaseContainerImage}

echo "Tagging image for stable ${stableContainerImage}"
docker tag ${localContainerImage} ${stableContainerImage}

echo "Pushing stable image"
docker push ${stableContainerImage}


echo ""
echo "Done"
echo ""


