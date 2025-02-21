FROM alpine:3.20
ENV SQLALCHEMY_DATABASE_URI="mysql+pymysql://usuario:password@endereco/banco"
COPY ./ /app
WORKDIR /app
RUN ls -a
RUN pip3 install -r requirements.txt
CMD [ "gunicorn", "wsgi:app", "--bind", "0.0.0.0:8000" ]