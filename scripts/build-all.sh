# Set the default label
: ${VERSION_LABEL:=dev}

echo "Will build corpustrends images with version <$VERSION_LABEL>. Set VERSION_LABEL to override this."

docker build -t instituutnederlandsetaal/corpustrends-server:$VERSION_LABEL server/ || { echo 'failed to build server, I refuse to continue the build' ; exit 1; }
docker build -t instituutnederlandsetaal/corpustrends-client:$VERSION_LABEL client/ || { echo 'failed to build client, I refuse to continue the build' ; exit 1; }
