import os


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', "notifications_db"),
        'USER': os.environ.get('POSTGRES_USER', "notifapp"),
        'PASSWORD': os.environ.get('DB_PASSWORD', "qwerty123"),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', 5432),
        'OPTIONS': {
           'options': '-c search_path=public,content'
        }
    }
}