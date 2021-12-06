#!/usr/bin/env bash
source ./.github/scripts/funcs.sh

ARTIFACT_DOMAIN="https://identity-artifact.iamdev.s.uw.edu"

function print_help {
   cat <<EOF
   Use: configure-workflow.sh [--debug --help]
   Options:
   --help -h      Show this message and exit
   --debug -g     Show commands as they are executing
EOF
}

while (( $# ))
do
  case $1 in
    --help|-h)
      print_help
      exit 0
      ;;
    --debug|-g)
      set -x
      ;;
    *)
      echo "Invalid Option: $1"
      print_help
      exit 1
      ;;
  esac
  shift
done

function get-workflow-snapshot-artifact() {
  local actor="$GITHUB_ACTOR"
  test -n "$actor" || actor="github-actions[bot]"
  local payload="<$(get-build-url) | Workflow> "
  local idp_env="$IDP_ENV"
  payload+="started by <https://github.com/$actor | @$actor> "
  if [[ -n "${INPUT_REASON}" ]]
  then
    payload+="with reason: \`$INPUT_REASON\` "
  fi
  payload+="| Commit <https://github.com/$GITHUB_REPOSITORY/commit/$GITHUB_SHA | $(get-short-sha)> "
  if [[ -n "${INPUT_TARGET_IDP_ENV}" ]]
  then
    payload+="| Target IdP env: ${INPUT_TARGET_IDP_ENV} "
  fi
  if [[ -n "${INPUT_TARGET_IDP_HOST}" ]]
  then
    payload+="| Target IdP host: ${INPUT_TARGET_IDP_HOST} "
  fi
  if [[ -n "${INPUT_PYTEST_ARGS}" ]]
  then
    payload+="| custom test arguments: \`${INPUT_PYTEST_ARGS}\` "
  fi
  echo "$payload"
}

function install-uwca-cert() {
    if [[ -z "${UWCA_CERT}" ]]
    then
        echo "No UWCA certificate is configured in the Action environment!"
        FAIL=1
       fi
    if [[ -z "${UWCA_CERT}" ]]
    then
        echo "No UWCA certificate key is configured in the Action environment!"
        FAIL=1
    fi
    test -z "${FAIL}" || return 1
    if ! echo "${UWCA_CERT}" | base64 -d > /tmp/uwca.crt
    then
        FAIL=1
        echo "::error::Could not install UWCA certificate; value is not stored as base64."
    else
        echo "Installed UWCA certificate"
    fi
    if ! echo "${UWCA_KEY}" | base64 -d > /tmp/uwca.key
    then
        FAIL=1
        echo "::error::Could not install UWCA certificate key; value is not stored as base64."
    else
        echo "Installed UWCA certificate key"
    fi
    echo "Validating UWCA cert/key . . ."
    set -x
    key_mod=$(openssl rsa -modulus -noout -in /tmp/uwca.key | openssl md5)
    cert_mod=$(openssl x509 -modulus -noout -in /tmp/uwca.crt | openssl md5)
    if [[ "${key_mod}" != "${cert_mod}" ]]
    then
        FAIL=1
        echo "::error::UWCA certificate and key do not match."
    fi
    set +x
    if [[ -n "${FAIL}" ]]
    then
        echo "::error::UWCA certificate installation unsuccessful"
    fi
}

function get-run-tests-args() {
  # Make sure the mount point is properly formatted for docker-compose;
  # if it's relative to the current directory, we must add `./`
  local report_mount_point="$1"
  if ! [[ "${report_mount_point:0:1}" =~ [\./] ]]
  then
    report_mount_point="./$report_mount_point"
  fi
  payload="--report-dir $report_mount_point"
  payload+=" --env $INPUT_TARGET_IDP_ENV"
  payload+=" --uwca-cert /tmp/uwca.crt"
  payload+=" --uwca-key /tmp/uwca.key"
  if [[ -n "${INPUT_TARGET_IDP_HOST}" ]]
  then
    payload+=" --strict-host ${INPUT_TARGET_IDP_HOST}"
  fi

  if [[ -n "$INPUT_PYTEST_ARGS" ]]
  then
    payload+=" +- ${INPUT_PYTEST_ARGS}"
  fi
  echo "$payload"
}

function configure-workflow() {
  local event_name="$GITHUB_EVENT_NAME"
  local actor="$GITHUB_ACTOR"
  local artifact_object_path=$(get-report-output-path $event_name)
  INPUT_TARGET_IDP_ENV="${INPUT_TARGET_IDP_ENV:-eval}"
  if ! install-uwca-cert
  then
    echo "Could not configure workflow; UWCA certificate and/or key is missing."
    return 1
  fi
  set-output report-object-path "$artifact_object_path"
  set-output report-url "$ARTIFACT_DOMAIN/$artifact_object_path/index.html"
  set-output short-sha "$(get-short-sha)"
  set-output pr-number "$(get-pr-number)"
  set-output workflow-id "$event_name/$actor/$(get-timestamp)"
  set-output workflow-snapshot-artifact "$(get-workflow-snapshot-artifact)"
  set-output idp-env "${INPUT_TARGET_IDP_ENV}"
  set-output idp-host "${INPUT_TARGET_IDP_HOST}"
  set-output run-tests-args "$(get-run-tests-args $artifact_object_path)"
  set-output slack-channel "${INPUT_SLACK_CHANNEL:-#iam-bots}"
}
