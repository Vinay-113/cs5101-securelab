FROM ubuntu:26.04
# Ubuntu's minimal OCI image need not include ps; explicitly add the lab tool.
RUN apt-get update && apt-get install -y --no-install-recommends procps \
    && rm -rf /var/lib/apt/lists/*
CMD ["ps", "-ef"]
