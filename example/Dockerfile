FROM ubuntu:jammy-20231211.1

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

WORKDIR /root/protoss

COPY . .

RUN cmake -Btarget . && cd target && cmake --build . && \
    cd ../
