FROM alpine:edge

RUN apk add --update py-pip
RUN apk add gcc python3-dev musl-dev postgresql-dev

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt

COPY Login_and_Register_Service.py /usr/src/app/

EXPOSE 5000

CMD ["python3", "/usr/src/app/Login_and_Register_Service.py"]