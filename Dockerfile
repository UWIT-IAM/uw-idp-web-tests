ARG SOURCE_TAG=latest
ARG DI=dependency-image
FROM ghcr.io/uwit-iam/poetry:${SOURCE_TAG} AS dependency-image
WORKDIR /uw-idp-tests
COPY poetry.lock pyproject.toml ./
ENV ALLOW_HOSTS_MODIFICATION "1"
RUN apt-get -y install curl jq dnsutils && poetry install

FROM $DI AS uw-idp-web-tests
COPY settings.yaml scripts/set-idp-host.sh scripts/wait-for-selenium.sh ./
COPY tests/ ./tests
