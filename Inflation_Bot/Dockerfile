FROM python:3.10-alpine3.17
LABEL 	version="1.0" \
		description="Telegram Bot designed to gather official Argentinian inflation information from https://datos.gob.ar/ via API." \
		mantainer="Lucas Gonzalez Zan" \
		email="lucasgonzalezzan@gmail.com"

# update your telegram token below
ENV TOKEN="1234567890:ABCDEFGHIJKMNLOPQRSTUVXYZabcdefghij"


ENV app=/app
WORKDIR ${app}   
COPY . .    
RUN adduser -D irobot && chown irobot:irobot ${app}/data/
USER irobot

CMD [ "python", "./bot.py" ]
