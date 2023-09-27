# MOVIES SERVICES
## Компоненты системы:
### Основные:
authapp/ - cервис регистрации/аутентификации/авторизации на flask. (AuthApi)\
fastapi-solution/ - сервис выдачи информации сайта о фильмах/жанрах/людях на fast-api. (MoviesApi)\
ugcservice/ - fast-api сервис, сохраняющий и отдающий ugc(user-generated content). (UGCStorageAsyncApi)\
[Панель менеджера/администратора(MoviesAdminPanel)](https://github.com/mybestnickname/django-movies-api)
### Рекомендательная система:
rec_service/ - fast-api сервис для получения/сохранения/выдачи рекомендаций пользователю. (RecommendationsAPI)\
recsys/ - Модель рекомендаций - SVD (single value decomposition); Метрика качества - RMSE. (RecommendationsService)
### Система рассылки уведомлений пользователям:
movies-services/notifications/django-admin-panel/ - панель администратора на django для создания шаблонов и заданий уведомлений. (DjangoAdminPanel)\
movies-services/notifications/fastapi-notification-service/ - fast-api сервис получения заданий на рассылку уведомлений, отправляющий их в RabbitMQ. (NotificationsApi)
### Прочее:
netflix_etl/ - скрипты для загрузки netflix данных в сервисы.\
[ETL процесс по переносу данных из PSQL в Elasticsearch(ETLProcess1)](https://github.com/mybestnickname/etl-process)\
ETL/ - процесс, перекладывающий данные из Kafka в ClickHouse. (ETLProcess2)\
movies-services/notifications/worker/ - Consumer, пересылающий уведомления из RabbitMQ к провайдеру рассылки. (Worker/Consumer)
## Архитектура взаимодействия микросервисов распределенного приложения:
![alt text](https://github.com/mybestnickname/movies-services/blob/master/scheme.png)
---
![alt text](https://github.com/mybestnickname/movies-services/blob/master/notifsystem.png)
---
![alt text](https://github.com/mybestnickname/movies-services/blob/master/recsystem.png)
***
## Installation
docker-compose up --build
## Init db
flask db upgrade
## Flask auth api OpenAPI Specification
localhost:8000/auth_api/doc/
## FastApi movies api OpenAPI Specification
localhost:8000/movies_api/openapi
## Create admin user
flask createsuperuser <email> <password>
## Clickhouse initialization
Execute code for nodes (node1, node3, node5) from clickhouse.ddl file
***

:octocat:
