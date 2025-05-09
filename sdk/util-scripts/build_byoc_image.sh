#!/bin/bash

set -e

# <set_variables>
ENDPOINT_NAME=$0
GROUP=$1
WORKSPACE=$2
LOCATION=$3

ASSET_PATH=../model-1 # Path to the model asset
DOCKERFILE_PATH=../cli/custom-container/fast-in-dockerfile/minimal-single-model-conda-in-dockerfile.dockerfile # Path to the Dockerfile
IMAGE_NAME=azureml-examples/minimal-single-model-fast2-in-dockerfile # Name of the image
IMAGE_TAG=1 # Tag of the image
# </set_variables>

# echo $ENDPOINT_NAME, $GROUP, $WORKSPACE, $LOCATION

# <az_configure_defaults>
az configure --defaults group=$GROUP workspace=$WORKSPACE location=$LOCATION
# </az_configure_defaults>

ACR_NAME=$(az ml workspace show --query container_registry -o tsv | cut -d'/' -f9-)

# <build_image_fast_in_dockerfile>
az acr build -f $DOCKERFILE_PATH -t $IMAGE_NAME:$IMAGE_TAG -r $ACR_NAME $ASSET_PATH
# </build_image_fast_in_dockerfile>

export BYOC_IMAGE_NAME_PATH=$ACR_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG
echo $BYOC_IMAGE_NAME_PATH
