FROM debian:jessie
ARG lepidopter_tag="v0.2.1-alpha"
ARG lepidopter_update_tag="master"

RUN apt-get update && apt-get install -y \
                    git \
                    python-pip \
                    sudo

RUN git clone -b $lepidopter_tag https://github.com/TheTorProject/lepidopter.git /opt/lepidopter/

RUN mkdir -p /integration
WORKDIR /integration

RUN git clone -b $lepidopter_update_tag https://github.com/OpenObservatory/lepidopter-update.git /integration/lepidopter-update
RUN lepidopter-update/tests/integration/lepidopter-install-${lepidopter_tag}.sh

CMD [ "python", "lepidopter-update/tests/integration/main.py" ]
