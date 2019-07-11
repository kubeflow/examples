"""Script to build and update the model.
Requires python3
hub CLI depends on an OAuth token with repo permissions:
https://hub.github.com/hub.1.html
  * It will look for environment variable GITHUB_TOKEN
"""

import datetime
import fire
import logging
import os
import pathlib
import re
import shutil
import tempfile
import yaml

import fire
import git
import httplib2

from kubeflow.testing import util # pylint: disable=no-name-in-module

class ModelUpdater(object): # pylint: disable=useless-object-inheritance
  def __init__(self):
    pass

  def _replace_parameters(self, lines, values):
    """Replace parameters in ksonnet text.
    Args:
      lines: Lines of text
      values: A dictionary containing the names of parameters and the values
        to set them to.
    Returns:
      lines: Modified lines
      old: Dictionary of old values for these parameters
    """
    old = {}
    for i, line in enumerate(lines):
      # Split the line on white space
      pieces = re.findall(r'\S+', line)

      # Check if this line is a parameter
      # // @optionalParam image string gcr.io/myimage Some image
      if len(pieces) < 5:
        continue

      if pieces[0] != "//" or pieces[1] != "@optionalParam":
        continue

      param_name = pieces[2]
      if not param_name in values:
        continue

      old[param_name] = pieces[4]
      logging.info("Changing param %s from %s to %s", param_name, pieces[4],
                   values[param_name])
      pieces[4] = values[param_name]

      lines[i] = " ".join(pieces)

    return lines, old

  def _clone_repo(self, src_dir):
    # Clone the repo
    repo_owner = "jlewi"
    repo_name = "kubecon-demo"
    org_dir = os.path.join(src_dir, "jlewi")
    repo_dir = os.path.join(org_dir, repo_name)
    if not os.path.exists(org_dir):
      os.makedirs(os.path.join(src_dir, repo_owner))

    if not os.path.exists(repo_dir):
      util.run(["git", "clone", "git@github.com:jlewi/kubecon-demo.git",
                repo_name], cwd=org_dir)

    repo = git.Repo(repo_dir)
    return repo

  def _update_deployment(self, repo_dir, model_file):
    """Update the prototype file.
    Args:
      repo_dir
      model_file: new model_file
    Returns:
      prototype_file: The modified prototype file or None if the image is
        already up to date.
    """
    deployment_file = os.path.join(repo_dir, "deployment", "model.yaml")

    with open(deployment_file) as hf:
      deploy_spec = yaml.load(hf)

    for i, v in enumerate(
      deploy_spec["spec"]["template"]["spec"]["containers"][0]["env"]):
      if v["name"] != "MODEL_FILE":
        continue

      v["value"] = model_file

    with open(deployment_file, "w") as hf:
      yaml.dump(deploy_spec, stream=hf)
    logging.info("Updated deploy_spec to %s", deploy_spec)

    return deployment_file

  def _find_remote_repo(self, repo, remote_url): # pylint: disable=no-self-use
    """Find the remote repo if it has already been added.
    Args:
      repo: The git python repo object.
      remote_url: The URL of the remote repo e.g.
        git@github.com:jlewi/kubeflow.git
    Returns:
      remote: git-python object representing the remote repo or none if it
        isn't present.
    """
    for r in repo.remotes:
      for u in r.urls:
        if remote_url == u:
          return r

    return None

  def _maybe_setup_ssh(self):
    """Maybe setup ssh."""
    ssh_dir = os.getenv("SSH_DIR")

    if not ssh_dir:
      logging.info("SSH_DIR environment variable not set; skipping ssh setup")
      return

    logging.info("Setting up ssh from %s", ssh_dir)
    ssh_home = os.path.join(pathlib.Path.home(), ".ssh")
    if not os.path.exists(ssh_home):
      os.makedirs(ssh_home)

    os.chmod(ssh_home, 0o700)
    for (dirpath, dirnames, filenames) in os.walk(ssh_dir):
      for f in filenames:
        src = os.path.join(dirpath, f)
        dest = os.path.join(ssh_home, f)
        logging.info("Copy %s to %s", src, dest)
        shutil.copyfile(src, dest)

        ext = os.path.splitext(f)[-1]

        if ext == "pub":
          mode = 0o644
        else:
          mode = 0o600

        logging.info("Set permissions on file %s to %s", dest, mode)
        os.chmod(dest, mode)

  def _add_github_hosts(self):
    if not self._add_github_to_known_hosts:
      return
    logging.info("Scanning and adding github hosts")
    output = util.run(["ssh-keyscan", "github.com"])

    with open(os.path.join(pathlib.Path.home(), ".ssh", "known_hosts"),
              mode='a') as hf:
      hf.write(output)

  def all(self, model_file, src_dir, remote_fork, # pylint: disable=too-many-statements,too-many-branches
          add_github_host=False):
    """Build the latest image and update the prototype.
    Args:
      model_file: The path to the model
      src_dir: Directory where source should be checked out
      remote_fork: Url of the remote fork.
        The remote fork used to create the PR;
         e.g. git@github.com:jlewi/kubeflow.git. currently only ssh is
         supported.
      add_github_host: If true will add the github ssh host to known ssh hosts.
    """
    self._maybe_setup_ssh()

    # Ensure github.com is in the known hosts
    self._add_github_to_known_hosts = add_github_host

    self._add_github_hosts()

    repo = self._clone_repo(src_dir)
    self._repo = repo
    util.maybe_activate_service_account()

    if not remote_fork.startswith("git@github.com"):
      raise ValueError("Remote fork currently only supports ssh")

    remote_repo = self._find_remote_repo(repo, remote_fork)

    if not remote_repo:
      fork_name = remote_fork.split(":", 1)[-1].split("/", 1)[0]
      logging.info("Adding remote %s=%s", fork_name, remote_fork)
      remote_repo = repo.create_remote(fork_name, remote_fork)

    now = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
    util.run(["git", "checkout", "-b", "update_model_" + now, "origin/master"],
             cwd=repo.working_dir)

    # rerun the scane for known hosts
    # Not sure why we need to rerun it but if we don't we get prompted about
    # unverified hosts
    self._add_github_hosts()
    deployment_file = self._update_deployment(repo.working_dir, model_file)

    if self._check_if_pr_exists(model_file):
      # Since a PR already exists updating to the specified commit
      # don't create a new one.
      # We don't want to just push -f because if the PR already exists
      # git push -f will retrigger the tests.
      # To force a recreate of the PR someone could close the existing
      # PR and a new PR will be created on the next cron run.
      return

    logging.info("Add file %s to repo", deployment_file)
    repo.index.add([deployment_file])
    repo.index.commit("Update the modelto {0}".format(model_file))

    util.run(["git", "push", "-f", remote_repo.name], cwd=repo.working_dir)

    self.create_pull_request(model_file=model_file)

  def _pr_title(self, model_file):
    pr_title = "[auto PR] Update the model to {0}".format(
      model_file)
    return pr_title

  def _check_if_pr_exists(self, model_file):
    """Check if a PR is already open.
    Returns:
      exists: True if a PR updating the image to the specified commit already
       exists and false otherwise.
    """
    # TODO(jlewi): Modeled on
    # https://github.com/kubeflow/examples/blob/master/code_search/docker/ks/update_index.sh
    # TODO(jlewi): We should use the GitHub API and check if there is an
    # existing open pull request. Or potentially just use the hub CLI.

    pr_title = self._pr_title(model_file)

    # See hub conventions:
    # https://hub.github.com/hub.1.html
    # The GitHub repository is determined automatically based on the name
    # of remote repositories
    output = util.run(["hub", "pr", "list", "--format=%U;%t\n"],
                      cwd=self._repo.working_dir)


    lines = output.splitlines()

    prs = {}
    for l in lines:
      n, t = l.split(";", 1)
      prs[t] = n

    if pr_title in prs:
      logging.info("PR %s already exists to update the model to "
                   "to %s", prs[pr_title], model_file)
      return True

    return False

  def create_pull_request(self, model_file, base="jlewi:master"):
    """Create a pull request.
    Args:
      model_file: Name of the model file to update to
      base: The base to use. Defaults to "kubeflow:master". This should be
        in the form <GitHub OWNER>:<branch>
    """
    pr_title = self._pr_title(model_file)

    with tempfile.NamedTemporaryFile(delete=False) as hf:
      hf.write(pr_title.encode())
      message_file = hf.name

    # TODO(jlewi): -f creates the pull requests even if there are local changes
    # this was useful during development but we may want to drop it.
    util.run(["hub", "pull-request", "-f", "--base=" + base, "-F",
              message_file],
              cwd=self._repo.working_dir)

if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO,
                      format=('%(levelname)s|%(asctime)s'
                              '|%(pathname)s|%(lineno)d| %(message)s'),
                      datefmt='%Y-%m-%dT%H:%M:%S',
                      )
  logging.getLogger().setLevel(logging.INFO)
  fire.Fire(ModelUpdater)