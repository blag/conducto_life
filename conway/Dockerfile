FROM python:3.8.3-alpine
COPY . /life
WORKDIR /life
RUN apk add bash jq ttf-liberation zlib-dev jpeg-dev gcc musl-dev freetype-dev
RUN pip install conducto
RUN python setup.py develop
