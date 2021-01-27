#! /bin/bash
APP_NAME=$1
FROM_LABEL=$2
TO_LABEL=$3
if [ -z $APP_NAME ] || [ -z $FROM_LABEL ] || [ -z $TO_LABEL ]; then
    echo "PLEASE SPECIFY AN APP_NAME: ${0} <OCP APP_NAME> <FROM_LABEL> <TO_LABEL>"
    exit
fi

IMAGES=($(oc get is -l app=${APP_NAME} | awk '{print $1}' | sed 1d))

for img in ${IMAGES[@]}; do
    oc tag ${img}:${FROM_LABEL} ${img}:${TO_LABEL}
done
