FROM python:3.9-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /base

COPY ./requirements.txt /base/
RUN apt-get update \
  && apt-get -y install ffmpeg \
  && apt-get -y install cron \
  && pip install -r requirements.txt
COPY ./bbcetc.cron /etc/cron.d/
RUN  chmod 0644 /etc/cron.d/bbcetc.cron \
  && crontab /etc/cron.d/bbcetc.cron
CMD bash -c 'mkdir -p /base/tmp \
    && mkdir -p /base/www \
    && touch /base/www/index.html \
    && env > /etc/environment \
    && cron -f'

