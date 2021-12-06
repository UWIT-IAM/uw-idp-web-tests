#!/usr/bin/env bash

function print_help {
   cat <<EOF
   Use: run-tests.sh [--debug --help]
   Options:
   --report-dir   Set the LOCAL directory where you want
                  the report output at the end (defaults to './webdriver-report')

   --no-build     Do not rebuild the image before running

   --strict-host  Provide this with an argument (e.g., "idp11") to route all
                  idp traffic to a single host.

   --uwca-cert/-uc  (Optional) The file name of the UWCA certificate that
                           is necessary to run certain tests. If this is set, then
                           --uwca-key must also be set; both files must be in the
                           same directory.

   --uwca-key/-uk          (Optional) The file name of the UWCA key that is necessary
                           to run certain tests. If this is set, then --uwca-cert
                           must also be set; both files must be in the same directory.

   -- [...]       All input after `--` will be sent to pytest as CLI arguments.
   +- [...]       All input after `+-` will be appended to default pytest CLI arguments.

   --source-tag   You may define a different image other than `latest`
                  for the base UWIT-IAM/poetry image here. (You shouldn't need to.)
   --report-id    Set the report artifact name (not yet used)
   --help/-h      Show this message and exit
   --debug/-g     Show commands as they are executing
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
      --uwca-cert|-uc)
        shift
        UWCA_CERT="${1}"
        ;;
      --uwca-key|-uk)
        shift
        UWCA_KEY="${1}"
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


function build_images() {
    set -e
    ./scripts/build-images.sh
    set +e
}


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
    PYTEST_ARGS+=" --settings-profile docker_compose"
  fi
  if ! [[ "${PYTEST_ARGS}" =~ '--report-dir' ]]
  then
    PYTEST_ARGS+=" --report-dir /tmp/webdriver-report"
  fi
  if ! [[ "${PYTEST_ARGS}" =~ '--env' ]]
  then
    PYTEST_ARGS+=" --env $IDP_ENV"
  fi
  if [[ -n "$UWCA_CERT" ]]
  then
    PYTEST_ARGS+=" --uwca-cert-filename /certificates/$(basename $UWCA_CERT)"
    PYTEST_ARGS+=" --uwca-key-filename /certificates/$(basename $UWCA_KEY)"
  fi
}

parse_args "$@" || exit 1
validate_env
sanitize_pytest_args
REQUIRED_COMPOSE_ARGS=${REQUIRED_COMPOSE_ARGS:-up --exit-code-from test-runner}

test -n "${NO_BUILD}" || build_images


export TARGET_IDP_HOST="${STRICT_HOST}"
export CREDENTIAL_MOUNT_POINT="$(dirname $GOOGLE_APPLICATION_CREDENTIALS)"
export CREDENTIAL_FILE_NAME="$(basename $GOOGLE_APPLICATION_CREDENTIALS)"

if [[ -n "${UWCA_CERT}" ]]
then
    export UWCA_MOUNT_POINT="$(dirname $UWCA_CERT)"
    UWCA_KEY_MOUNT_POINT="$(dirname $UWCA_KEY)"

    if [[ "${UWCA_KEY_MOUNT_POINT}" != "${UWCA_MOUNT_POINT}" ]]
    then
        echo "Cannot mount a certificate and key from different directories."
        echo "Either remove those arguments or place both files in the "
        echo "same directory and try again."
        echo "place both files in the same directory and try again."
        echo "UWCA_CERT=${UWCA_CERT}"
        echo "UWCA_KEY=${UWCA_KEY}"
        exit 1
    fi
else
    mount_dir="/tmp/idp-mount"
    mkdir -pv "${mount_dir}"
    # This just mounts an empty directory in readonly mode as a placeholder
    # otherwise docker-compose would fail because of an empty volume source.
    export UWCA_MOUNT_POINT="${mount_dir}"
fi

export PYTEST_ARGS="${PYTEST_ARGS}"
export TEST_ARTIFACT_OBJECT_NAME="${REPORT_ID}"
export REPORT_MOUNT_POINT=${REPORT_MOUNT_POINT:-./webdriver-report}

rm -vf $REPORT_MOUNT_POINT/worker.*  # Clean up workers from a previous run if it
                                     # exited too early
test -z "$STRICT_HOST" || add_strict_host_override "$STRICT_HOST"
COMPOSE_ARGS+=" $REQUIRED_COMPOSE_ARGS"
docker-compose ${COMPOSE_ARGS}
