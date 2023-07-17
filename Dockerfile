FROM python:3.10
COPY src/ . 
WORKDIR /app
RUN python -m pip install --upgrade pip
RUN pip install dist/cc_default_ml_nitin7478-0.0.5-py3-none-any.whl
EXPOSE 8000
CMD gunicorn --workers=4 --bind 127.0.0.1:8000 app:app
