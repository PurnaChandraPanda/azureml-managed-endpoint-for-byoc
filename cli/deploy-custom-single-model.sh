#!/bin/bash

set -e

# <set_variables>
export LOCATION="eastus2" # Location of the azureml workspace
export GROUP="rg-mlws" # Name of the resource group with azureml workspace
export WORKSPACE="mlws01" # Name of the azureml workspace
export ENDPOINT_NAME="customfastep" # Partial name of the endpoint to ceate

export BASE_PATH=custom-container # Location of deployment yaml files
export ASSET_PATH=../model-1 # Location of the model files
# </set_variables>

# <az_configure_defaults>
az configure --defaults group=$GROUP workspace=$WORKSPACE location=$LOCATION
# </az_configure_defaults>

## Set random endpoint name
ENDPOINT_NAME=$ENDPOINT_NAME-`echo $RANDOM`

## Get the container registry name
ACR_NAME=$(az ml workspace show --query container_registry -o tsv | cut -d'/' -f9-)

## Helper function to change parameters in yaml files
change_vars() {
  for FILE in "$@"; do 
    TMP="${FILE}_"
    cp $FILE $TMP 
    readarray -t VARS < <(cat $TMP | grep -oP '{{.*?}}' | sed -e 's/[}{]//g'); 
    for VAR in "${VARS[@]}"; do
      sed -i "s/{{${VAR}}}/${!VAR}/g" $TMP
    done
  done
}

# <create_endpoint>
change_vars $BASE_PATH/minimal-single-model-endpoint.yml
az ml online-endpoint create -f $BASE_PATH/minimal-single-model-endpoint.yml_
# </create_endpoint>

rm $BASE_PATH/minimal-single-model-endpoint.yml_

# Get key and url 
echo "Getting access key and scoring URL..."
KEY=$(az ml online-endpoint get-credentials -n $ENDPOINT_NAME --query primaryKey -o tsv)
SCORING_URL=$(az ml online-endpoint show -n $ENDPOINT_NAME --query scoring_uri -o tsv)
echo "Scoring url is $SCORING_URL"

# <build_image_fast_in_dockerfile>
az acr build -f $BASE_PATH/fast-in-dockerfile/minimal-single-model-conda-in-dockerfile.dockerfile -t azureml-examples/single-model-fast1-in-dockerfile:1 -r $ACR_NAME $ASSET_PATH
# </build_image_fast_in_dockerfile>

# <create_deployment_fast_in_dockerfile>
DEPLOYMENT_YML=$BASE_PATH/fast-in-dockerfile/minimal-single-model-conda-in-dockerfile-deployment.yml 
change_vars $DEPLOYMENT_YML
az ml online-deployment create --endpoint-name $ENDPOINT_NAME -f "${DEPLOYMENT_YML}_" --all-traffic
# </create_deployment_fast_in_dockerfile> 

rm $BASE_PATH/fast-in-dockerfile/*.yml_

## read base url
### remove everything after the last /
BASE_URL=${SCORING_URL%/*}
echo "Base URL is $BASE_URL"
echo "Scoring URL is $SCORING_URL"

# <test_deployment_conda_in_dockerfile>
sleep 2
echo " "
curl -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" "${BASE_URL}/"

sleep 2
echo " "
curl -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" "${BASE_URL}/score1"

sleep 2
echo " "
curl -X POST -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" -d @$ASSET_PATH/test-data/request.json $SCORING_URL

sleep 2
echo " "
curl -X POST -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" -d @$ASSET_PATH/test-data/sample-request.json "${BASE_URL}/predict"

sleep 2
echo " "
# </test_deployment_conda_in_dockerfile>


# <delete_online_endpoint>
# az ml online-endpoint delete -y -n $ENDPOINT_NAME
# </delete_online_endpoint>
