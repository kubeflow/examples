#!/bin/bash 

while (($#)); do
   case $1 in
     "--numPs")
       shift
       numPs="$1"
       shift
       ;;
     "--numWorkers")
       shift
       numWorkers="$1"
       shift
       ;;
     "--help")
       shift
       echo "Usage: ./definition.sh --numPs number_of_PS --numWorkers number_of_worker"
       shift
       ;;
     *)
       echo "Unknown argument: '$1'"
       echo "Usage: ./definition.sh --numPs number_of_PS --numWorkers number_of_worker"
       exit 1
       ;;
   esac
done

if [ "x${numPs}" != "x" ]; then
  if [[ ${numPs} =~ ^[0-9]+$ ]] && [ ${numPs} -gt 0 ]; then
    sed -i.sedbak s/%numPs%/${numPs}/  ps.yaml >> /dev/null
    kustomize edit add patch ps.yaml 
  else
    echo "ERROR: numPS must be an integer greater than or equal to 1."
    exit 1
  fi 
fi

if [ "x${numWorkers}" != "x" ]; then
  if [[ ${numWorkers} =~ ^[0-9]+$ ]] && [ ${numWorkers} -gt 0 ]; then
    sed -i.sedbak s/%numWorkers%/${numWorkers}/ worker.yaml >> /dev/null
    kustomize edit add patch worker.yaml 
  else
    echo "ERROR: numWorkers must be an integer greater than or equal to 1."
    exit 1
  fi 
fi

rm -rf *.sedbak 
