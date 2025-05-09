set -e

# <set_variables>
ENDPOINT_NAME=$1
GROUP=$2
WORKSPACE=$3
LOCATION=$4
ASSET_PATH=$5
# </set_variables>

# <az_configure_defaults>
az configure --defaults group=$GROUP workspace=$WORKSPACE location=$LOCATION
# </az_configure_defaults>

## Get key and url 
echo "Getting access key and scoring URL..."
KEY=$(az ml online-endpoint get-credentials -n $ENDPOINT_NAME --query primaryKey -o tsv)
SCORING_URL=$(az ml online-endpoint show -n $ENDPOINT_NAME --query scoring_uri -o tsv)

## read base url
### remove everything after the last /
BASE_URL=${SCORING_URL%/*}
echo "Base URL is $BASE_URL"
echo "Scoring URL is $SCORING_URL"


# <test_deployment_conda_in_dockerfile>
sleep 2
echo " "
echo "${BASE_URL}/"
curl -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" "${BASE_URL}/"

sleep 2
echo " "
echo "${BASE_URL}/score1"
curl -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" "${BASE_URL}/score1"

sleep 2
echo " "
echo $SCORING_URL
curl -X POST -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" -d @$ASSET_PATH/request.json $SCORING_URL

sleep 2
echo " "
echo "${BASE_URL}/predict"
curl -X POST -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" -d @$ASSET_PATH/sample-request.json "${BASE_URL}/predict"

sleep 2
echo " "
# </test_deployment_conda_in_dockerfile>

