  
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8


COPY ./src /app/src
COPY requirements.txt /app/src

WORKDIR /app/src

RUN pip3 install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host=0.0.0.0", "--reload"]