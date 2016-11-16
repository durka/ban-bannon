import os
import sys

sys.path.append('/home/ubuntu/website')

os.environ['PYTHON_EGG_CACHE'] = '/home/ubuntu/website/.python-egg'

from website.wsgi import application

