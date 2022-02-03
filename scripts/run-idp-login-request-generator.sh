function print_help {
   cat <<EOF
   Use: run-idp-testing-tool.sh [--debug --help]
   Options:
   -n, --num-login-attempts The number of login/logout cycles to attempt
   -z, --login-attempt-wait-time-secs   How long to wait between each login attempt
   -ip, --idp-ip   (Optional) A strict IP to send all idp requests through.
   -b, --build     If used, will build a new image to run the test
   -h, --help      Show this message and exit
   -g, --debug     Show commands as they are executing
EOF
}

num_login_attempts=1
sleep_time=5
image=ghcr.io/uwit-iam/idp-web-tests:lb-test

function parse_args {
  while (( $# ))
  do
    case $1 in
      --help|-h)
        print_help
        exit 0
        ;;
      -n|--num-login-attempts)
        shift
        num_login_attempts="$1"
        ;;
      -z|--login-attempt-wait-time-secs)
        shift
        sleep_time="$1"
        ;;
      -ip|--idp-ip)
        shift
        idp_ip="$1"
        ;;
      -b|--build)
        force_build=1
        ;;
      --debug|-g)
        DEBUG=1
        ;;
      *)
        echo "Invalid Option: $1"
        print_help
        exit 1
        ;;
    esac
    shift
  done

test -z "${DEBUG}" || set -x
export DEBUG="${DEBUG}"
}

parse_args "$@"

if [[ -z "${force_build}" ]]
then
  docker pull ${image}
  docker tag ${image} ghcr.io/uwit-iam/idp-web-tests:build
fi

./scripts/run-tests.sh \
  --env prod \
  $(test -z "${idp_ip}" || echo "--strict-ip ${idp_ip}") \
  $(test -n "${force_build}" || echo "--no-build") \
  +- --skip-test-service-provider-start --skip-test-service-provider-stop \
  --lb-num-loops ${num_login_attempts} --lb-sleep-time ${sleep_time} \
  tests/test_generate_requests.py
