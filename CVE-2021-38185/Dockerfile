FROM kalilinux/kali-rolling

ARG DEBIAN_FRONTEND=noninteractive

RUN apt update
RUN apt install -y git python3-dev python3-pip sudo
RUN apt install -y gdb
RUN apt install -y vim    
RUN apt install -y gcc-multilib
RUN apt install -y build-essential
RUN apt install -y libssl-dev
RUN apt install -y libffi-dev
RUN apt install -y libxml2-dev
RUN apt install -y libxslt1-dev
RUN apt install -y zlib1g-dev
RUN apt install -y patchelf 
RUN apt install -y cpio

RUN pip3 install pwntools 

RUN git clone https://github.com/pwndbg/pwndbg && cd pwndbg && chmod +x ./setup.sh && ./setup.sh && cd ..

CMD ["/bin/bash"]