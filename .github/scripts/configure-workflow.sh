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
  payload+="| Commit <https://github.com/$GITHUB_REPOSITORY/commit/$GITHUB_SHA | $(get-short-sha)>"
  echo "$payload"
}

function configure-workflow() {
  local event_name="$GITHUB_EVENT_NAME"
  local actor="$GITHUB_ACTOR"
  local artifact_object_path=$(get-report-output-path $event_name)
  set-output report-object-path "$artifact_object_path"
  set-output report-url "$ARTIFACT_DOMAIN/$artifact_object_path/index.html"
  set-output short-sha "$(get-short-sha)"
  set-output pr-number "$(get-pr-number)"
  set-output workflow-id "$event_name/$actor/$(get-timestamp)"
  set-output workflow-snapshot-artifact "$(get-workflow-snapshot-artifact)"
}
