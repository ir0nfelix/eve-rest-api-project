FROM alpine:3.12

RUN addgroup -S -g 777 eve && adduser -D -S -G eve -u 777 eve

RUN apk update && apk upgrade && apk add python3 python3-dev build-base bash py3-pip && pip3 install --upgrade pip setuptools

ADD https://bin.equinox.io/c/ekMN3bCZFUn/forego-stable-linux-amd64.tgz /forego-stable-linux-amd64.tgz
RUN tar x -z -f forego-stable-linux-amd64.tgz && mv forego /usr/local/bin && rm forego-stable-linux-amd64.tgz

ENV TZ=Europe/Moscow
RUN apk add tzdata && cp /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN mkdir -p /restaurant_ms
WORKDIR /restaurant_ms

COPY ./requirements.txt /restaurant_ms/
RUN pip3 install -r requirements.txt

RUN apk del python3-dev build-base

COPY ./env.sh /env.sh
COPY ./start.sh /start.sh
RUN chown eve /start.sh /env.sh && chmod +x /start.sh /env.sh

COPY . /restaurant_ms/

RUN chown -R eve:eve /restaurant_ms

EXPOSE 5000

CMD ["/start.sh"]
