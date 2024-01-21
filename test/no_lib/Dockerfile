FROM ubuntu:22.04

WORKDIR /root

RUN apt update && apt -y install cmake \
    g++ libmysqlclient-dev wget unzip \
    libmysqlclient-dev build-essential && \
    wget https://github.com/fmtlib/fmt/releases/download/10.2.1/fmt-10.2.1.zip && \
    unzip fmt-10.2.1.zip

WORKDIR /root/fmt-10.2.1

RUN cmake -Bout && cd out && \
    cmake --build . && cmake --install .

RUN mkdir -p /home/user
RUN apt -y install mysql-client

WORKDIR /home/user

COPY main.cpp poc.cpp
COPY init.sql init.sql

RUN g++ -o poc poc.cpp -lfmt -lmysqlclient

CMD [ "/bin/tail", "-f", "/dev/null" ]