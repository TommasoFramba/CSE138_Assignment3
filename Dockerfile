FROM python:3.8.8
COPY . /app
RUN pip install requests
RUN make /app
WORKDIR /app
CMD python3 replica.py