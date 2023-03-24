FROM ubuntu:focal as base

# Install dependencies
RUN apt-get -qy update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -qqy \
        cmake \
        make \
        gcc \
        g++ \
        pkg-config \
        libzmq3-dev libczmq-dev \
        libboost-program-options-dev \
        #libvolk1-dev \
        libfftw3-dev \
        libmbedtls-dev \
        libsctp-dev \
        libyaml-cpp-dev \
        libgtest-dev \
        libconfig++-dev \
        curl \
        net-tools \
        telnet \
        iperf \
        iperf3\
        iputils-ping \
        iproute2 \
        iptables \
        git \
        unzip && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /srsran

# Pinned git commit used for this example (release 21.10)
# ARG COMMIT=5275f33360f1b3f1ee8d1c4d9ae951ac7c4ecd4e
# ARG COMMIT=51351190de263e27145ec4f2ae659b0ba628f5a5
# Download and build
# RUN curl -LO https://github.com/srsran/srsRAN/archive/${COMMIT}.zip && \
#     unzip ${COMMIT}.zip && \
#     rm ${COMMIT}.zip
# RUN apt-get install git
RUN git clone https://github.com/srsran/srsRAN_4G.git
# WORKDIR /srsran/srsRAN-${COMMIT}/build
WORKDIR /srsran/srsRAN_4G/build

RUN cmake -DENABLE_ZEROMQ=ON -DENABLE_UHD=OFF -DENABLE_BLADERF=OFF -DENABLE_SOAPYSDR=OFF .. && \
    make -j$(nproc --ignore=2) && \
    make install

# Update dynamic linker
RUN ldconfig

WORKDIR /srsran

# Copy all .example files and remove that suffix
# RUN cp srsRAN-${COMMIT}/*/*.example ./ && \
#     bash -c 'for file in *.example; do mv "$file" "${file%.example}"; done'

# Run commands with line buffered standard output
# (-> get log messages in real time)
ENTRYPOINT [ "stdbuf", "-oL" ]
