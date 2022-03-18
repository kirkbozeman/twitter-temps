Useful docker commands:

```
docker build -t big-health-tweet-app:latest .
docker build --no-cache -t big-health-tweet-app:latest .
docker exec -it $(docker ps -q --filter ancestor=big-health-tweet-app:latest) /bin/bash
docker stop $(docker ps -q --filter ancestor=big-health-tweet-app:latest)
docker-compose up
```