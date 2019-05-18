FROM archlinux/base

MAINTAINER AsAsgard

RUN pacman -Sy --noconfirm python-pip

ENV TZ=Europe/Moscow
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

COPY . /authentifiction

WORKDIR /authentifiction
RUN pwd

RUN pip install -r ./requirements/production.txt

CMD ["python", "run.py"]
