# base image
FROM python:3.7.3-alpine

# nuevo
# install dependencies
RUN apk update && \
  apk add --virtual build-deps gcc python-dev musl-dev && \
  apk add postgresql-dev && \
  apk add netcat-openbsd

# estableciendo directorio de trabajo
WORKDIR /usr/src/app

# copiando e instalando requerimientos
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# nuevo
# copiando entrypoint.sh
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

# copiando la app
COPY . /usr/src/app

# run server
CMD ["sh","-c","chmod 755 /usr/src/app/entrypoint.sh && /usr/src/app/entrypoint.sh"]
