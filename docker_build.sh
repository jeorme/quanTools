docker build --name jeromePetit -t pricev1:latest .
docker -p 8080:5000 pricev1:latest
docker login -u jvp2015 -p Fxinvjp79
docker tag pricev1 jvp2015/pricev1:2.0
docker push jvp2015/pricev1:2.0
