FROM ubuntu:22.04@sha256:149d67e29f765f4db62aa52161009e99e389544e25a8f43c8c89d4a445a7ca37

ENV LANG en_US.utf8
ENV TZ=Aisa/Seoul
ENV ZIGPATH=/opt/zig
ENV PWNDBG_VENV_PATH=/venv

RUN useradd user

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    apt-get update && \
    apt-get install -y locales && \
    rm -rf /var/lib/apt/lists/* && \
    localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8 && \
    apt-get update && \
    apt-get install -y vim socat mysql-server git

RUN git clone https://github.com/pwndbg/pwndbg && \
    cd pwndbg && ./setup.sh

# Add .gdbinit to the home folder of both root and vscode users (if vscode user exists)
# This is useful for a VSCode dev container, not really for test builds
RUN if [ ! -f ~/.gdbinit ]; then echo "source /pwndbg/gdbinit.py" >> ~/.gdbinit; fi && \
    if id -u ${LOW_PRIVILEGE_USER} > /dev/null 2>&1; then \
    su ${LOW_PRIVILEGE_USER} -c 'if [ ! -f ~/.gdbinit ]; then echo "source /pwndbg/gdbinit.py" >> ~/.gdbinit; fi'; \
    fi

RUN mkdir /home/user

COPY libs/ /home/user/libs
COPY flag_1 /flag_1
COPY protoss /home/user/protoss
COPY init.sql /home/user/init.sql

RUN chmod +x /home/user/protoss
RUN chmod 440 /flag_1
RUN chown user:root /home/user/*

WORKDIR /home/user

COPY signin .

CMD socat TCP-LISTEN:5050,reuseaddr,fork EXEC:"./protoss"
