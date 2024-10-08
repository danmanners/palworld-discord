FROM docker.io/library/python:3.13-alpine3.19 as builder

WORKDIR /opt
COPY requirements.txt requirements.txt
COPY bot.py bot.py

RUN pip install -r requirements.txt && \
    apk add --no-cache binutils && \
    pyinstaller bot.py --onefile --clean

FROM docker.io/library/alpine:3.19 as runtime
WORKDIR /opt
COPY --from=builder /opt/dist/bot bot
ENTRYPOINT [ "/opt/bot" ]
