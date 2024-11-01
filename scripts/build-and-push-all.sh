# Set the default label
: ${VERSION_LABEL:=dev}

./scripts/build-all.sh

echo "Will push corpustrends images with version <$VERSION_LABEL>. Set VERSION_LABEL to override this."

docker push instituutnederlandsetaal/corpustrends-server:$VERSION_LABEL
docker push instituutnederlandsetaal/corpustrends-client:$VERSION_LABEL
