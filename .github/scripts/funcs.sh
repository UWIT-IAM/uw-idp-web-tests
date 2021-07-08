#!/usr/bin/env bash

# Github Actions do not provide easy access to
# the PR number, so we have to extract it from
# a different environment variable payload.
function get-pr-number() {
    test -z "$GITHUB_EVENT_PATH" && return 1
    jq --raw-output .pull_request.number "$GITHUB_EVENT_PATH"
}


function get-timestamp() {
  TZ="US/Pacific" date +'%Y.%m.%d-%H.%M.%S'
}

function get-short-sha() {
  echo ${GITHUB_SHA:0:10}
}

function get-build-url() {
  echo "https://www.github.com/$GITHUB_REPOSITORY/actions/runs/$GITHUB_RUN_ID"
}

function get-report-output-path() {
  local event_name="$1"
  local prefix="web-tests/idp/$event_name"
  case $event_name in
    push)
      echo "$prefix/$(get-short-sha)"
      ;;
    pull_request)
      echo "$prefix/$(get-pr-number)"
      ;;
    schedule)
      echo "$prefix/$(get-timestamp)"
      ;;
    workflow_dispatch)
      echo "$prefix/$GITHUB_ACTOR/$(get-timestamp)"
      ;;
    *)
      echo "$prefix/$(get-timestamp)"
      ;;
  esac
}

function set-output() {
  local output_name="$1"
  local payload="$2"
  echo "::set-output name=$output_name::$payload"
}
