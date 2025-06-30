FROM kivy/buildozer:latest

WORKDIR /app
COPY . /app

RUN buildozer android debug

CMD ["cp", "bin/*.apk", "/output/"]
