FROM ubuntu:jammy-20231211.1



WORKDIR /root/protoss

COPY . .

RUN cmake -Btarget . && cd target && cmake --build . && \
    cd ../
