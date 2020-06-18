FROM python:3-slim as base

FROM base AS builder

COPY requirements.txt .

RUN pip install --user -r requirements.txt

# Running image
FROM base

# Setup the non root user and paths
RUN useradd --user-group -M mesa 
USER mesa
ENV PATH=/home/mesa/.local/bin:$PATH

# Mesa server port
EXPOSE 8521/tcp

# Copy build artefacts
COPY --from=builder --chown=mesa:mesa /root/.local /home/mesa/.local
COPY --chown=mesa:mesa run.py /app/
COPY --chown=mesa:mesa BaselineEconomy /app/BaselineEconomy/

WORKDIR /app

CMD ["/usr/local/bin/python3", "run.py", "global"]
