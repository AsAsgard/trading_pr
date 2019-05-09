FROM archlinux/base

MAINTAINER AsAsgard

RUN pacman -Sy --noconfirm python-pip

ENV TZ=Europe/Moscow
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

COPY . /request_handler

WORKDIR /request_handler
RUN pwd

RUN pip install -r ./requirements/production.txt

CMD ["python", "manage.py", "runserver", "-p5343", "-h0.0.0.0", "-D"]
