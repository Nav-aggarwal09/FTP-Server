FROM python:3.7

WORKDIR /usr/src/server/

# importing python code files
COPY controller.py ${WORKDIR}
COPY server.py ${WORKDIR}

VOLUME /serverdata

CMD ["python", "./controller.py"]

