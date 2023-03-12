FROM python:3.10-alpine3.17
LABEL 	version="1.0" \
		description="Telegram Bot designed to spell out using Italian cities and output a voice message with the spelling in Italian." \
		mantainer="Lucas Gonzalez Zan" \
		email="lucasgonzalezzan@gmail.com"

# update your telegram token below
ENV TOKEN="1234567890:ABCDEFGHIJKMNLOPQRSTUVXYZabcdefghij"


ENV app=/app
WORKDIR ${app}   
COPY . .    
RUN adduser -D irobot
USER irobot

CMD [ "python", "./bot.py" ]
