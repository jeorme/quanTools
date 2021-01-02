#!/bin/bash
# Ask the user for their name
while getopts "v:i:b:" optname
  do
    case "$optname" in
      "v")
        echo "version $OPTARG is specified"
        version=$OPTARG
        ;;
    esac
  done

docker login -u jvp2015 -p Fxinvjp79
docker images
docker build -t pricev1:$version .
docker run -d -p 5000:5000 pricev1:$version
docker-machine ip
docker tag pricev1:$version jvp2015/pricev1:$version
docker push jvp2015/pricev1:$version

##ibm part
#ibmcloud login -u jerome.petit@outlook.com -p Jeorme79$
#ibmcloud cs region-set uk-south
#ibmcloud cr login
#ibmcloud cr namespace-add pricev1
#docker tag jvp2015/pricev1:$version registry.eu-gb.bluemix.net/pricev1/pricev1:$version
#docker push registry.eu-gb.bluemix.net/pricev1/pricev1:$version
#ibmcloud cr image-list
#ibmcloud cs cluster-config cluster_pricev1
#kubectl get nodes
#kubectl create -f deployment.yaml
#kubectl create -f service.yaml
