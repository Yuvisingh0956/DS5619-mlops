# Docker verification

Fill this in after you build and run your container (see README.md,
"Part 2 — Dockerfile"). This is how we confirm your container actually works, since an
automated grader running in a sandbox may not always have Docker-in-Docker
available.

## Build

Paste the command you ran and its final output line (the one showing the
built image ID/tag):

```
docker build -t week6-detector .

Final output:

=> => writing image sha256:84e21c538f5dc90071f609587b5d96b8555a7965de2e8a1e215bcdb2fc1f6b06
=> => naming to docker.io/library/week6-detector
```

## Run

Paste the command you used to start the container (should map a host port
to the container's 8080):

```
ocker run --rm -p 8080:8080 week6-detector

Container output:

 * Serving Flask app 'app'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8080
 * Running on http://172.17.0.2:8080
Press CTRL+C to quit
172.17.0.1 - - [17/Sep/2026 15:12:36] "GET /health HTTP/1.1" 200 -
172.17.0.1 - - [17/Sep/2026 15:12:47] "POST /detect HTTP/1.1" 200 -
```

## Verify

Paste the exact `curl` commands and their JSON output for both endpoints,
run against the running container (not against `python src/app.py` directly
— the point is to prove the *container* works):

```
curl http://localhost:8080/health

{"status":"ok"}

curl -F "image=@data/fixtures/camera_A_daylight/000.jpg" http://localhost:8080/detect

{"count":2,"detections":[{"bbox":[16,63,26,12],"category_id":4,"id":0,"image_id":0,"score":0.98},{"bbox":[274,116,20,16],"category_id":12,"id":1,"image_id":0,"score":0.98}]}
```
