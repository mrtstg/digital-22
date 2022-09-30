FROM python:3.10-slim
RUN apt-get update && apt-get install make -y
COPY . .
RUN make venv
RUN make migrate
CMD make run
