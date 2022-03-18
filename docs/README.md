### Directions to run

1) Please create a file called `.env` in the root directory of the repo. Here you will add the following environment variables that will be utilized by Docker compose:
```angular2html
TWITTER_TOKEN=<YOUR_TWITTER_API_TOKEN>
WEATHER_TOKEN=<YOUR_WEATHER_API_TOKEN>
```

2. Please make sure Docker (https://www.docker.com/) is installed and running on your local machine.  


3. Please build the image:

```angular2html
docker build -t kirks-bh-tweet-app:latest .
```

4. Please run the image:

```angular2html
docker-compose up
```

5. The image will create a folder in your home directory called `output/` that will contain process output files.  


6. To end it all, hit `ctr+C` in the terminal or use `docker ps` to locate the container ID and use `docker stop <image ID>`.

Hey, here are some useful docker commands:

```
docker build -t big-health-tweet-app:latest .
docker build --no-cache -t big-health-tweet-app:latest .
docker exec -it $(docker ps -q --filter ancestor=big-health-tweet-app:latest) /bin/bash
docker stop $(docker ps -q --filter ancestor=big-health-tweet-app:latest)
docker-compose up
```