from .base import *

SECRET_KEY = env('DJANGO_SECRET_KEY', default='b+%@+jji%t)u7kqi$np+4e+mfs%cprrsy*s)mtglm6i_l7!-si')
DEBUG = env.bool('DJANGO_DEBUG', True);
