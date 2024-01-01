FROM ubuntu:22.04@sha256:149d67e29f765f4db62aa52161009e99e389544e25a8f43c8c89d4a445a7ca37

ENV LANG en_US.utf8
ENV TZ=Asia/Seoul
ENV ZIGPATH=/opt/zig
ENV PWNDBG_VENV_PATH=/venv
ENV LDFLAGS="-Wl,--copy-dt-needed-entries"
ENV BUILD_TYPE="Release"

WORKDIR /root

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    apt-get update && \
    apt-get install -y locales && \
    rm -rf /var/lib/apt/lists/* && \
    localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8 && \
    apt-get update && \
    apt-get install -y vim git socat mysql-server

# Package update & Install required package
RUN apt -y upgrade && apt -y install libssl-dev \
    libpthread-stubs0-dev zlib1g-dev \
    build-essential autoconf automake \
    libtool curl make g++ unzip wget git python3-pip && \
    wget https://github.com/Kitware/CMake/archive/refs/tags/v3.28.1.tar.gz && \
    tar xvf v3.28.1.tar.gz

# Build CMake & Install
RUN cd CMake-3.28.1 && ./bootstrap && \
    make -j$(nproc) && make install && \
    cp bin/* /usr/bin/

WORKDIR /root

# Build Protobuf & Install
RUN git clone https://github.com/protocolbuffers/protobuf.git && \
    cd protobuf && git checkout 2b79738d5f84aa37226b4ac2bc0210e672d07191 && \
    git submodule update --init --recursive && \
    cmake . -Bbuild -DCMAKE_BUILD_TYPE="${BUILD_TYPE}" \
    -DCMAKE_INSTALL_PREFIX="/usr/local/" -Dprotobuf_BUILD_SHARED_LIBS=ON \
    -Dprotobuf_BUILD_TESTS=OFF -Dprotobuf_ABSL_PROVIDER="module" \
    -Dprotobuf_BUILD_LIBPROTOC=OFF -DABSL_PROPAGATE_CXX_STD=ON  && \
    cd build && cmake --build . -- -j$(nproc) && cmake --install . && mkdir /root/protoss \
    && ldconfig && pip3 install protobuf

RUN mkdir /home/user/chall /home/user/protoss

COPY libs/ /home/user/chall/libs
COPY flag_1 /flag_1
COPY protoss /home/user/chall/protoss
COPY init.sql /home/user/chall/init.sql

RUN chmod +x /home/user/chall/protoss && chmod 440 /flag_1

WORKDIR /home

RUN git clone https://github.com/pwndbg/pwndbg && \
    cd pwndbg && DEBIAN_FRONTEND=noninteractive ./setup.sh && \
    if [ ! -f ~/.gdbinit ]; then echo "source /pwndbg/gdbinit.py" >> ~/.gdbinit; fi && \
    if id -u ${LOW_PRIVILEGE_USER} > /dev/null 2>&1; then \
        su ${LOW_PRIVILEGE_USER} -c 'if [ ! -f ~/.gdbinit ]; then echo "source /pwndbg/gdbinit.py" >> ~/.gdbinit; fi'; \
    fi

WORKDIR /home/user/protoss/

COPY protoss.proto .
COPY CMakeLists.txt .
COPY main.cpp .

RUN cmake -Btarget . && cd target && cmake --build . && \
    cd ../

CMD socat TCP-LISTEN:5050,reuseaddr,fork EXEC:"/home/user/chall/protoss"
