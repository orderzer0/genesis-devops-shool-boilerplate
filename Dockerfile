FROM python:3.8


WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

RUN pip install mysql-connector-python pandas

COPY . /app

EXPOSE 8081

CMD ["python", "api.py"]