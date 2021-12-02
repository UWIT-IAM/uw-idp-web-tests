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
   if [[ -n "${UWCA_CERT}" ]]
   then
       echo "${UWCA_CERT}" | base64 -d > /tmp/uwca.crt
       echo "Installed UWCA certificate"
   fi
   if [[ -n "${UWCA_KEY}" ]]
   then
       echo "${UWCA_KEY}" | base64 -d > /tmp/uwca.key
       echo "Installed UWCA certificate key"
   fi
}

function configure-pytest-args() {
  local payload="${INPUT_PYTEST_ARGS}"
  if [[ -n "${UWCA_CERT}" ]]
  then
    payload+=" --uwca-cert-filename /tmp/uwca.crt"
  fi
  if [[ -n "${UWCA_KEY}" ]]
  then
    payload+=" --uwca-key-filename /tmp/uwca.key"
  fi
  echo "${payload}"
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
  if [[ -n "${INPUT_TARGET_IDP_HOST}" ]]
  then
    payload+=" --strict-host ${INPUT_TARGET_IDP_HOST}"
  fi

  local pytest_args="$(configure-pytest-args)"
  if [[ -n "$pytest_args" ]]
  then
    payload+=" +- ${pytest_args}"
  fi
  echo "$payload"
}

function configure-workflow() {
  local event_name="$GITHUB_EVENT_NAME"
  local actor="$GITHUB_ACTOR"
  local artifact_object_path=$(get-report-output-path $event_name)
  INPUT_TARGET_IDP_ENV="${INPUT_TARGET_IDP_ENV:-eval}"
  install-uwca-cert
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
