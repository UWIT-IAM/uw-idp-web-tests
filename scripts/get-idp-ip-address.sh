#!/usr/bin/env bash

function print_help {
   cat <<EOF
   Use: get-idp-ip-address.sh [--debug --help]
   Options:
   --help/-h      Show this message and exit
   --debug/-g     Show commands as they execute
   --env/-e       The target env (eval/prod)
   --host/-t      The target host (ip address will be looked up) in the
                  form of idpXX (e.g., idp14, idpeval11)
EOF
}

HOST_IP=
EXIT_STATUS=0


function get_host_ip() {
  local host="$1"
  if [[ -z "$host" ]]
  then
    return 0
  fi
  if [[ "$host" =~ idp(eval)?[0-9]+ ]]
  then
    host="$host.s.uw.edu"
  else
    echo "ERROR: Invalid host format."
    print_help
    return 1
  fi
  echo "$(dig +short $host)"
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
    --host|-t)
      shift
      HOST=$1
      if [[ -n "$HOST" ]]
      then
        HOST_IP="$(get_host_ip "$HOST")"
        EXIT_STATUS=$?
      fi
      ;;
    *)
      echo "Invalid Option: $1"
      print_help
      exit 1
      ;;
  esac
  shift
done

if [[ "$EXIT_STATUS" == "0" ]] && [[ -z "$HOST_IP" ]]
then
  echo "No ip address found for $HOST"
  EXIT_STATUS=1
fi

echo $HOST_IP
exit $EXIT_STATUS
