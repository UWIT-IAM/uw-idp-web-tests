ARG SOURCE_TAG=latest
ARG DI=dependency-image
FROM ghcr.io/uwit-iam/poetry:${SOURCE_TAG} AS dependency-image
ENV ALLOW_HOSTS_MODIFICATION "1"
RUN apt-get -y install curl jq dnsutils

FROM $DI as poetry-di
WORKDIR /uw-idp-tests
COPY poetry.lock pyproject.toml ./
RUN poetry install

FROM poetry-di AS uw-idp-web-tests
COPY settings.yaml scripts/wait-for-selenium.sh ./
COPY tests/ ./tests
