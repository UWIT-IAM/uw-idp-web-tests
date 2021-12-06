
./scripts/install-build-scripts.sh

image_name="ghcr.io/uwit-iam/idp-web-tests:latest"

function build_images() {
  set -ex
  docker build --build-arg SOURCE_TAG \
    --cache-from "${image_name}" \
    -t "${image_name}" .
  set +ex
}

build_images
