FROM debian:jessie
ARG lepidopter_tag="v0.2.1-alpha"

RUN apt-get update && apt-get install -y \
                    git \
                    python-pip \
                    sudo

RUN git clone -b $lepidopter_tag https://github.com/TheTorProject/lepidopter.git /opt/lepidopter/

RUN mkdir -p /integration
WORKDIR /integration

COPY lepidopter-install-${lepidopter_tag}.sh /integration
RUN /integration/lepidopter-install-${lepidopter_tag}.sh

COPY main.py /integration/

CMD [ "python", "main.py" ]
