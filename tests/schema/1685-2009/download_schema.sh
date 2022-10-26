#!/bin/bash

this_dir="$( cd "$(dirname "$0")" ; pwd -P )"
cd $this_dir

base=http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009

wget -nc -nv --tries=5 \
    ${base}/abstractionDefinition.xsd \
    ${base}/abstractor.xsd \
    ${base}/autoConfigure.xsd \
    ${base}/busDefinition.xsd \
    ${base}/busInterface.xsd \
    ${base}/commonStructures.xsd \
    ${base}/component.xsd \
    ${base}/configurable.xsd \
    ${base}/constraints.xsd \
    ${base}/design.xsd \
    ${base}/designConfig.xsd \
    ${base}/file.xsd \
    ${base}/fileType.xsd \
    ${base}/generator.xsd \
    ${base}/identifier.xsd \
    ${base}/index.xsd \
    ${base}/memoryMap.xsd \
    ${base}/model.xsd \
    ${base}/port.xsd \
    ${base}/signalDrivers.xsd \
    ${base}/simpleTypes.xsd \
    ${base}/subInstances.xsd
