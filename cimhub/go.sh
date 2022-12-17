#!/bin/bash
source envars.sh
rm -rf dss
mkdir dss
rm -rf glm
mkdir glm
curl -D- -X POST $DB_URL --data-urlencode "update=drop all"
curl -D- -H "Content-Type: application/xml" --upload-file ./Master.xml -X POST $DB_URL
java -cp $CIMHUB_PATH $CIMHUB_PROG -u=$DB_URL -o=dss  -l=1.0 -p=1.0 -e=carson dss/Master
java -cp $CIMHUB_PATH $CIMHUB_PROG -u=$DB_URL -o=glm  -l=1.0 -p=1.0 -e=carson glm/Master
