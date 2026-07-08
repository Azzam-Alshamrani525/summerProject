# some commands
# to build the docker

docker build -t week1-day5 .
# to run docker

docker run -it --name summerize_run -e GEMINI_API_KEY=$GEMINI_API_KEY week1-day5 summerize.py

# to copy the file from the docker to your device

docker cp summerize_run:/app/summary.pdf ./summary.pdf
docker cp summerize_run:/app/summarize.txt ./summarize.txt

# Clean up the container after each run (so the name is free next time)
docker rm summerize_run
