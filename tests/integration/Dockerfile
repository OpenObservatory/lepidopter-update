FROM debian:jessie
ARG lepidopter_tag="v0.2.1-alpha"

RUN apt-get update && apt-get install -y \
                    git \
                    python-pip \
                    sudo

RUN git clone -b $lepidopter_tag https://github.com/TheTorProject/lepidopter.git /opt/lepidopter/
ADD lepidopter-install-${lepidopter_tag}.sh
RUN lepidopter-install-${lepidopter_tag}.sh

RUN service lepidopter-updater stop

RUN mkdir -p /integration
WORKDIR /integration
COPY main.py /integration/

CMD [ "python", "main.py" ]
