FROM python:3.7.2

RUN mkdir -p /usr/src/bot

WORKDIR /usr/src/bot

COPY . /usr/src/bot
RUN pip3 install --no-cache-dir pyTelegramBotAPI python-cinderclient python-glanceclient python-keystoneclient python-neutronclient python-novaclient python-openstackclient json-logging enum34 pysocks

CMD [ "python", "/usr/src/bot/bot.py" ]