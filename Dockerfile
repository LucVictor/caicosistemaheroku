FROM python:3.9
ENV SQLALCHEMY_DATABASE_URL="BANCO"
COPY ./ /app
WORKDIR /app
RUN ls -a
RUN pip3 install -r requirements.txt
CMD [ "gunicorn", "wsgi:app", "--bind", "0.0.0.0:8000" ]
