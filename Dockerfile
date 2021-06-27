FROM python:3.9-slim

RUN \
  mkdir /src && \
  cd src && \
  pip install -U pip && \
  pip install \
  django \
  graphene-django \
  graphene-file-upload \
  pillow \
  django-cors-headers \
  django-filter \
  django-graphql-jwt \
  pyjwt==1.7.0 \
  python-decouple \
  dj-database-url \
  cloudinary \
  django-cloudinary-storage \
  psycopg2-binary \
  gunicorn

CMD [ "/bin/bash" ]