# Yatube
Yatube - социальная сеть для публикации блогов, с возможностью постить как в общую ленту, так и в группы по интересам. Имеет возможность подписываться на интересных авторов.
***

## Стек технологий
Python 3.7+, Django 2.2.6, unittest, pytest

### Настройка и запуск на ПК

Клонируем проект:

```bash
git clone https://github.com/epselont/hw05_final.git
```

или

```bash
git clone git@github.com:epselont/hw05_final.git
```

Переходим в папку с проектом:

```bash
cd hw05_final
```

Устанавливаем виртуальное окружение:

```bash
python -m venv venv
```

Активируем виртуальное окружение:

```bash
source venv/Scripts/activate
```

> Для деактивации виртуального окружения выполним (после работы):
> ```bash
> deactivate
> ```

Устанавливаем зависимости:

```bash
python -m pip install --upgrade pip
```
```bash
pip install -r requirements.txt
```

Применяем миграции:

```bash
python yatube/manage.py makemigrations
python yatube/manage.py migrate
```

Создаем супер пользователя:

```bash
python yatube/manage.py createsuperuser
```

Запускаем проект:

```bash
python yatube/manage.py runserver localhost:80
```

После чего проект будет доступен по адресу http://localhost/

Заходим в http://localhost/admin и создаем группы и записи.
После чего записи и группы появятся на главной странице.
## Тесты
#### Тесты запускаются командой:
    python manage.py test
#### или командой:
    pytest
