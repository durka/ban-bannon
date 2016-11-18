This is a website dedicated to helping US citizens call their Congressional representatives to demand denouncement of Steve Bannon's appointment to chief strategist for President-elect Donald Trump.

## HACKING

OSX installation:

```
brew install python3 libxml2
pip3 install Django==1.10.3 requests==2.12.0 beautifulsoup4==4.5.1 django-memoize==2.0.0
pip3 install --global-option=build_ext --global-option=-L/usr/local/opt/libxml2/lib --global-option=build_ext --global-option=-I/usr/local/opt/libxml2/include/libxml2 lxml==3.6.4
```

Linux installation:

```
sudo apt-get install python3 python3-pip libxml2-dev libxslt-dev lib32z1-dev
sudo pip3 install Django==1.10.3 requests==2.12.0 beautifulsoup4==4.5.1 lxml==3.6.4 django-memoize==2.0.0
```

Server setup ([source](https://www.linode.com/docs/websites/nginx/use-uwsgi-to-deploy-Python-apps-with-nginx-on-ubuntu-12-04)):

```
sudo apt-get install nginx-full uwsgi uwsgi-plugin-python3
```

To run things locally, copy the `local_settings.py` file into `webserver/webserver`, and then:

```
cd website
python3 manage.py runserver
```
