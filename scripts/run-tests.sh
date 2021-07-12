#!/usr/bin/env bash

function print_help {
   cat <<EOF
   Use: run-tests.sh [--debug --help]
   Options:
   --help/-h      Show this message and exit
   --debug/-g     Show commands as they are executing
   --report-id    Set the report artifact name (not yet used)
   --report-dir   Set the LOCAL directory where you want
                  the report output at the end
   --no-build     Do not rebuild the image before running
   --strict-host  Provide this with an arugment (e.g., "idp11") to route all
                  idp traffic to a single host.
   --source-tag   You may define a different image other than `latest`
                  for the base UWIT-IAM/poetry image
   -- [...]       All input after `--` will be sent to pytest as CLI arguments.
   +- [...]       All input after `+-` will be appended to default pytest CLI arguments.
EOF
}

export PYTEST_ARGS="${PYTEST_ARGS:-"-o log_cli=true -o log_cli_level=info"}"
test -z "$PYTEST_EXT_ARGS" || PYTEST_ARGS="${PYTEST_ARGS} ${PYTEST_EXT_ARGS}"

IDP_ENV=eval

function parse_args() {
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
      --env|-e)
        shift
        IDP_ENV=$1
        ;;
      --report-id)
        shift
        TEST_ARTIFACT_OBJECT_NAME="$1"
        ;;
      --report-dir)
        shift
        REPORT_MOUNT_POINT="$1"
        ;;
      --no-build)
        NO_BUILD=1
        ;;
      --source-tag)
        shift
        export SOURCE_TAG=$1
        ;;
      --strict-host)
        shift
        STRICT_HOST=$1
        ;;
      --)
        shift
        export PYTEST_ARGS="$@"
        return
        ;;
      +-)
        shift
        PYTEST_ARGS+=" $@"
        return
        ;;
      *)
        echo "Invalid Option: $1"
        print_help
        return 1
        ;;
    esac
    shift
  done
}

parse_args "$@" || exit 1

if [[ -z "${NO_BUILD}" ]]
then
  set -e
  docker build --build-arg SOURCE_TAG -t ghcr.io/uwit-iam/idp-web-tests:build .
  set +e
fi

function add_strict_host_override() {
  local host="$1"
  local ip=$(./scripts/get-idp-ip-address.sh -g -t "$host")
  if [[ "$?" -gt "0" ]]
  then
    echo $ip
    return 1
  fi

  compose_override="strict-host-override.docker-compose.yml"
  local host="idp.u.washington.edu"
  if [[ "$IDP_ENV" == "eval" ]]
  then
    host="idp-eval.u.washington.edu"
  fi
  export EXTRA_HOST="$host:$ip"
  COMPOSE_ARGS+=" -f docker-compose.yml -f $compose_override"
}

function validate_env() {
  FAILED=
  test -n "${GOOGLE_APPLICATION_CREDENTIALS}" || FAILED=1
  if [[ -n "$FAILED" ]]
  then
    echo "Cannot create test environment. You must provide the
    GOOGLE_APPLICATION_CREDENTIALS environment variable."
    exit 1
  fi

}


function sanitize_pytest_args() {
  if ! [[ "${PYTEST_ARGS}" =~ '--settings-profile' ]]
  then
    PYTEST_ARGS="$PYTEST_ARGS --settings-profile docker_compose"
  fi
  if ! [[ "${PYTEST_ARGS}" =~ '--report-dir' ]]
  then
    PYTEST_ARGS="$PYTEST_ARGS --report-dir /tmp/webdriver-report"
  fi
  if ! [[ "${PYTEST_ARGS}" =~ '--env' ]]
  then
    PYTEST_ARGS="$PYTEST_ARGS --env $IDP_ENV"
  fi
}

validate_env
sanitize_pytest_args

REQUIRED_COMPOSE_ARGS=${REQUIRED_COMPOSE_ARGS:-up --exit-code-from test-runner}

export TARGET_IDP_HOST="${STRICT_HOST}"
export CREDENTIAL_MOUNT_POINT="$(dirname $GOOGLE_APPLICATION_CREDENTIALS)"
export CREDENTIAL_FILE_NAME="$(basename $GOOGLE_APPLICATION_CREDENTIALS)"
export PYTEST_ARGS="${PYTEST_ARGS}"
export TEST_ARTIFACT_OBJECT_NAME="${REPORT_ID}"
export REPORT_MOUNT_POINT=${REPORT_MOUNT_POINT:-./webdriver-report}
rm -vf $REPORT_MOUNT_POINT/worker.*  # Clean up workers from a previous run if it
                                     # exited too early
test -z "$STRICT_HOST" || add_strict_host_override "$STRICT_HOST"
COMPOSE_ARGS+=" $REQUIRED_COMPOSE_ARGS"
docker-compose ${COMPOSE_ARGS}
