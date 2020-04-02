# Build docker file

echo "Build time: $(date)"
echo "------------------------------------------"

docker kill covid19
docker rm covid19
docker build -t lachmann12/covid19 .
docker push lachmann12/covid19
docker run -p 8089:5000 --name covid19 lachmann12/covid19
