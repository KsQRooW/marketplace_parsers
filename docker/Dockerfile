FROM python:3.10
COPY ../requirements.txt /opt/api/requirements.txt
WORKDIR /opt/api
RUN pip install -r requirements.txt
RUN pip install -U "celery[redis]"
COPY .. /opt/api
CMD ["python", "main.py"]
