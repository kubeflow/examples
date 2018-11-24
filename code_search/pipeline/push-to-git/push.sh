#!/usr/bin/env bash

set -ex


usage()
{
    echo "usage: push.sh
    [--gcs_file The GCS file to be pushed ]
    [--git_repo The git repository to push the file to ]
    [--user_email The email account to use for pushing the change ]
    [-h help]"
}

while [ "$1" != "" ]; do
    case $1 in
      --gcs_file )
        shift
        GCS_FILE=$1
        ;;
      --git_repo )
        shift
        GIT_REPO=$1
        ;;
      -h | --help )
        usage
        exit
        ;;
      * )
        usage
        exit 1
    esac
    shift
done

git config --global user.email pipeline@localhost
git clone https://${GIT_TOKEN}@github.com/${GIT_REPO}.git repo
cd repo && gsutil cp ${GCS_FILE} . && git add * && git commit -m "index update" && git push origin master


