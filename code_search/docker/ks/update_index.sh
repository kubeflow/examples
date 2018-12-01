#!/bin/bash
#
# This script creates a PR updating the nmslib index used by search-index-server.
# It uses ks CLI to update the parameters.
# After creating and pushing a commit it uses the hub github CLI to create a PR.
set -ex

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" > /dev/null && pwd)"

branch=master

usage() {
	echo "Usage: update_index.sh
	--baseGitRepo=<base git repo name>
	--baseBranch=<base branch>
	--appDir=<ksonnet app dir>
	--forkGitRepo=<github repo with Argo CD hooked up>
	--env=<ksonnet environment>
	--indexFile=<index file>
	--lookupFile=<lookup file>
	--workflowId=<workflow id invoking the container>
	--botEmail=<email account of the bot that send the PR>"
}

# List of required parameters
names=(baseGitRepo baseBranch appDir forkGitRepo env indexFile lookupFile workflowId botEmail)

source "${DIR}/parse_arguments.sh"

if [ ! -z ${help} ]; then
	usage
fi

if [ -z ${dryrun} ]; then
	dryrun=false
fi


git config --global user.email ${botEmail}
git clone https://${GITHUB_TOKEN}@github.com/${forkGitRepo}.git repo && cd repo/${appDir}
git config credential.helper store
git remote add upstream https://github.com/${baseGitRepo}.git
git fetch upstream
git merge upstream/${baseBranch} master

git checkout -b ${workflowId}
ks param set --env=${env} search-index-server indexFile ${indexFile}
ks param set --env=${env} search-index-server lookupFile ${lookupFile}
git add . && git commit -m "Update the lookup and index file."

FILE=$(mktemp tmp.create_pull_request.XXXX)

cat <<EOF >$FILE
Update the lookup and index file by pipeline ${workflowId}

This PR is automatically generated by update_index.sh.

This PR updates the index and lookup file used to serve
predictions.
EOF

# Create a pull request
if (! ${dryrun}); then
    git push origin ${workflowId}
    hub pull-request --base=${baseGitRepo}:${baseBranch} -F ${FILE}
else
	echo "dry run; not committing to git."
fi
