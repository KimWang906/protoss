FROM ubuntu:22.04@sha256:149d67e29f765f4db62aa52161009e99e389544e25a8f43c8c89d4a445a7ca37

RUN useradd user

RUN apt-get update
RUN apt-get install -y socat mysql-server

RUN mkdir /home/user

COPY libs/ /home/user/libs
COPY flag_1 /flag_1
COPY protoss /home/user/protoss
COPY init.sql /home/user/init.sql

RUN chmod +x /home/user/protoss
RUN chmod 440 /flag_1
RUN chown user:root /home/user/*

WORKDIR /home/user

CMD socat TCP-LISTEN:5050,reuseaddr,fork EXEC:"./protoss"
