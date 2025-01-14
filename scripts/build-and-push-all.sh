# Set the default label
: ${VERSION_LABEL:=dev}

./scripts/build-all.sh

echo "Will push woordpeiler images with version <$VERSION_LABEL>. Set VERSION_LABEL to override this."

docker push instituutnederlandsetaal/woordpeiler-server:$VERSION_LABEL
docker push instituutnederlandsetaal/woordpeiler-client:$VERSION_LABEL
