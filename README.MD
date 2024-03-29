
Collection and visualization movie information
=================================================================================================================

### Discleimer!
Проект створено з навчальною метою, аби отримати практику з написання python скриптів, які б дозволили запускати їх паралельно на різних машинах, що дозволить масштабувати рішення, використовувати сховище даних для зберігання json даних, візуалізувати данні використовуючи python бібліотеки та запускати цей процес на окремих машинах за допомогою технології контейнеризації

## Опис версії v.0.10
- Проект розроблений для створення процесу збору даних з зовнішнього ресурсу, зберігання в сховище та візуалізації на веб сервері 
- Джерело даних о фільмах є веб-сайт з можливостю отримати дані в json форматі по API виклику
- Збір даних виконує python скрипт, який спроектований для паралельного виконування на різних машинах для масштабування 
- Сховищем зібраних даних є Postgres база даних
- Візуалізацію даних у вигляді графіка, реалізує веб сервер платформи streamlit
- Запуск процесу реалізується за допомогою Docker кластера (три машини для збирання даних Python скриптом, одна машина сховище, одна машина веб сервер візуалізації)
- Було створено python скрипти для зібрання наступної інформації: кількість фільмів по рокам; кількість фільмів 4 жанрів по рокам; всі фільми (перші 500 сторінок даних, це ліміт API, одна сторінка 20 фільмів, то в році збирається перші 10,000 фільмів);
- По замовченню система виконує скрипт, який збирає і візуалізує кількість фільмів 4 жанрів по рокам


## Інструкція з запуску середовища.

#### Перед запуском слід переконатись, що на робочій машині у вас встановлено:
 - Docker https://docs.docker.com/get-docker/
  
### Крок 1. Запускаємо кластер контейнерів за допомогою *docker compose*
Переходимо в папку mdb_cluster та виконуємо команду:
```
docker compose up -d
```
чи запускаємо скрипт 
```
run-cluster.bat
```


### Крок 2. Чекаємо поки запуститься сховище

Перевірити, що дані зберігаються в сховище успішно можна за допомогою лога роботи контейнерів "gen_data_app1..3"  
```
docker logs -f gen_data_app1
```
чи запускаємо скрипт 
```
show-logs-gen_apps.bat
```

### Крок 3. Перегляд візуалізації даних
Відкриваємо веб додаток у браузері, переходимо localhost:8501 та дивимось як росте графік з 1900 року до 2024 року
Посилання:
```
http://localhost:8501/
```

## Додаткові артефакти проекту
Проект дозволяє зібрати таку інформацію за допомогою скриптів:

#### Кількість фільмів по рокам
- Збір даних: mdb_cluster\gen_app\app\gen_data.py 
- Візуалізація: mdb_cluster\vis_app\app\visapp.py 

#### Кількість фільмів 4 жанрів по рокам 
- Збір даних: mdb_cluster\gen_app\app\gen_list_data.py 
- Візуалізація: mdb_cluster\vis_app\app\visapp_list_data.py 

#### Всі фільми по рокам 
- Збір даних: mdb_cluster\gen_app\app\pulling_all_movie.py 
- Візуалізація: mdb_cluster\vis_app\app\visapp_status_loading_by_page.py  

### Для зміни даних, що збираються требо прописати посилання на ці скрипти в такі файли:
- Збір даних в файл mdb_cluster\gen_app\Dockerfile в частину "CMD"
- Візуалізація: mdb_cluster\vis_app\app\Dockerfile в частину "CMD"

