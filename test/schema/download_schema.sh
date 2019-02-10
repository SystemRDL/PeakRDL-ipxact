#!/bin/bash

this_dir="$( cd "$(dirname "$0")" ; pwd -P )"
cd $this_dir

base=http://www.accellera.org/XMLSchema/IPXACT/1685-2014

wget -nc -nv \
    ${base}/abstractionDefinition.xsd \
    ${base}/abstractor.xsd \
    ${base}/autoConfigure.xsd \
    ${base}/busDefinition.xsd \
    ${base}/busInterface.xsd \
    ${base}/catalog.xsd \
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
    ${base}/subInstances.xsd \
    ${base}/xml.xsd
