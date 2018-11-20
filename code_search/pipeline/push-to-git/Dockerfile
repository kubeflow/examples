FROM google/cloud-sdk

RUN apt-get install -y -qq --no-install-recommends sudo && \
    curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash && \
    sudo apt-get install git-lfs && \
    git lfs install

ADD pipeline/push-to-git/push.sh /usr/local/src
# ADD pipeline/push-to-git/.gotattributes /root

WORKDIR /usr/local/src

ENTRYPOINT ["/usr/local/src/push.sh"]