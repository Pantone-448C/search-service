FROM python:3.9.7

COPY ./ /usr/share/api
WORKDIR /usr/share/api
RUN pip3 install -r requirements.txt

ENTRYPOINT [ "python3", "./main.py"]