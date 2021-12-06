#!/usr/bin/env bash

export BUILD_SCRIPTS_DIR="./.build-scripts"

if [[ "$*" =~ -f|--force ]] || ! [[ -f "${BUILD_SCRIPTS_DIR}/.VERSION" ]]
then
  bash <(curl -Lsk https://uwiam.page.link/install-build-scripts)
fi
