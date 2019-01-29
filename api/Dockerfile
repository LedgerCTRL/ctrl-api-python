FROM python:3.6.6

# download and build solidity from source
WORKDIR /tmp
RUN apt-get update
RUN apt-get install sudo
RUN git clone --recursive https://github.com/ethereum/solidity.git \
&& cd solidity \
&& git checkout tags/v0.4.24 \
#&& sed 's/sudo//g' ./scripts/install_deps.sh > ./scripts/install_deps_nosudo.sh \
#&& sed 's/sudo//g' ./scripts/build.sh > ./scripts/build_nosudo.sh \
&& ./scripts/install_deps.sh
RUN sed -i 's/make -j2/make -j1/g' /tmp/solidity/scripts/build.sh && /tmp/solidity/scripts/build.sh

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

EXPOSE 8088

ENTRYPOINT ["python3"]

CMD ["-m", "swagger_server"]
