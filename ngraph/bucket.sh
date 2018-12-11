#!/bin/bash

usage () 
{
  echo -e "Usage: $0 [OPTIONS] COMMANDS\n"\
  'OPTIONS:\n'\
  '  -h       | --help       \n'\
  'COMMANDS:\n'\
  '  create   <bucket-name>\n'\
  '  delete   <bucket-name>\n'
  '  list     <bucket-name>\n'
}

error()
{
  echo $1
  exit 1
}

if [[ $# == 0 ]]; then
  usage
  exit 1
fi

createbucket()
{
  local bucket=$1 email=$2
  gsutil mb gs://${bucket}/ && \
  gsutil acl ch -u ${email}:O gs://$bucket
}

deletebucket()
{
  local bucket=$1
  gsutil rm -R gs://${bucket}/* 2>&1 >/dev/null
  gsutil rb -f gs://$bucket
}

deletebuckets()
{
  local me=$(whoami) bucket
  for i in $(listbuckets|grep $me); do
    bucket=${i:5:$((${#i}-4-2))}
    echo "deleting $bucket ..."
    deletebucket $bucket
  done
}

listbuckets()
{
  gsutil ls
}

commands () 
{
  if [[ $# == 0 ]]; then
    usage
    exit 1
  fi
  while :
  do
    case "$1" in
      create)
        shift 1
        createbucket $@
        break;
        ;;
      delete)
        shift 1
        case "$1" in 
          all)
            deletebuckets $@
            ;;
          *)
            deletebucket $@
            ;;
        esac
        break;
        ;;
      list)
        shift 1
        listbuckets $@
        break;
        ;;
      *)
        echo "**** unknown argument $1 ****"
        exit 1
        break
        ;;  
    esac
  done
}

while :
do
  case "$1" in
    -h | --help)
	  usage
	  exit 0
	  ;;
    --) 
      shift
      break
      ;;
    -*)
      echo "Error: Unknown option: $1" >&2
      exit 1
      ;;
    *) 
      break
      ;;
  esac
done
commands $*
