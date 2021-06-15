FROM python:3.8

RUN mkdir /app 

COPY /wireguy /app/wireguy
COPY pyproject.toml /app 
WORKDIR /app

ENV PYTHONPATH=${PYTHONPATH}:${PWD} 
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

RUN mkdir /data && chown nobody /data
VOLUME ["/data"]

USER nobody
EXPOSE 8000
CMD ["gunicorn", "whois.web:app", "-b 0.0.0.0:8000"]
