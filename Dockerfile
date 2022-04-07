FROM ghcr.io/uwit-iam/poetry:latest AS apt-base
ENV ALLOW_HOSTS_MODIFICATION "1"
RUN apt-get update && apt-get -y install curl jq dnsutils

FROM apt-base as poetry-base
WORKDIR /uw-idp-tests
COPY poetry.lock pyproject.toml scripts/entrypoint.sh ./
RUN poetry install

FROM poetry-base AS test-runner
COPY settings.yaml ./
COPY tests/ ./tests
ENTRYPOINT ["/uw-idp-tests/entrypoint.sh"]
