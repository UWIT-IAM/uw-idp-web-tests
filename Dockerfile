# The poetry image is built often, so pinning to avoid breaking changes
FROM ghcr.io/uwit-iam/poetry:2025.04.02T012232 AS apt-base
ENV ALLOW_HOSTS_MODIFICATION="1"
RUN apt-get update && apt-get -y install curl jq dnsutils

FROM apt-base AS poetry-base
WORKDIR /uw-idp-tests
COPY poetry.lock pyproject.toml scripts/entrypoint.sh ./
RUN poetry install --no-root

FROM poetry-base AS test-runner
COPY settings.yaml ./
COPY tests/ ./tests
ENTRYPOINT ["/uw-idp-tests/entrypoint.sh"]
