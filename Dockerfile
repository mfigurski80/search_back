# base image is python:3, but then auto-install dependencies
FROM python:3-onbuild

# specify port
EXPOSE 5000

CMD ["python",'./flaskscript.py']
