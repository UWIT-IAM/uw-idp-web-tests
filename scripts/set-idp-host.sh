#!/usr/bin/env bash

function print_help {
   cat <<EOF
   Use: set-idp-host.sh [--debug --help]
   Options:
   --help/-h      Show this message and exit
   --debug/-g     Show commands as they are executing
   --host/-t      The target host (ip address will be looked up) in the
                  form of idpXX (e.g., idp14).
   --env/-e       'prod' or 'eval'; the idp endpoint to route to
EOF
}

HOST_IP=
TARGET_ENV=prod


function get_host_ip() {
  local host="$1"
  if [[ -z "$host" ]]
  then
    return 0
  fi
  if [[ "$host" =~ idp[0-9]+ ]]
  then
    host="$host.s.uw.edu"
  else
    echo "--host/-t argument must be in the form of idpXX (e.g., "idp14");"
    echo "  you entered '$host'"
    return 1
  fi
  echo "$(dig +short $host)"
}


function configure_environment() {
  local idp_domain_prefix=
  if [[ "$TARGET_ENV" == 'eval' ]]
  then
    idp_domain_prefix='-eval'
  fi
  IDP_DOMAIN="idp${idp_domain_prefix}.u.washington.edu"
  HOSTS_LINE="$HOST_IP $IDP_DOMAIN"
}


while (( $# ))
do
  case $1 in
    --help|-h)
      print_help
      exit 0
      ;;
    --host|-t)
      shift
      if [[ -n "$1" ]]
      then
        HOST_IP="$(get_host_ip "$1")"
        if [[ "$?" -gt "0" ]]
        then
          echo "$HOST_IP"
          exit 1
        elif [[ -z "$HOST_IP" ]]
        then
          echo "No IP address found for $1"
          exit 1
        else
          echo "Found IP $HOST_IP for host $1"
        fi
      fi
      ;;
    --env|-e)
      shift
      TARGET_ENV=$1
      ;;
    *)
      echo "Invalid Option: $1"
      print_help
      exit 1
      ;;
  esac
  shift
done

if [[ -z "$HOST_IP" ]]
then
  echo "No host provided; nothing to do!"
  exit 0
fi



configure_environment

if [[ -z "${ALLOW_HOSTS_MODIFICATION}" ]]
then
  echo "This script should only be run inside a docker container."
  echo "Use the following command to amend your personal /etc/hosts file:"
  echo
  echo "    sudo echo \"$HOSTS_LINE\" >> /etc/hosts"
  echo
  echo "You are responsible for cleaning up your own work station!"
else
  echo "Routing all traffic bound for $IDP_DOMAIN to IP $HOST_IP"
  echo "$HOSTS_LINE" >> /etc/hosts
fi
