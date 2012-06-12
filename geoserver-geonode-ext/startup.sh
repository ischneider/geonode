#!/bin/bash
if [ $GS_DATA != '' ]; then
  DATA_DIR="-DGEOSERVER_DATA_DIR=$GS_DATA"
fi
MAVEN_OPTS="-Xmx512m -XX:MaxPermSize=256m -XX:CompileCommand=exclude,net/sf/saxon/event/ReceivingContentHandler.startElement" mvn jetty:run $DATA_DIR
