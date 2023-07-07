## Установка:

Клонируем проект:  

    git clone https://github.com/anza-afk/social_media_api_test_task.git  

Создаём .env файл с переменными (как в файле с примером .env_example):

    SECRET_KEY (Сгенерированный "openssl rand -hex 32" секретный ключ)
    ALGORITHM (Алгоритм шифрования токена)
    ACCESS_TOKEN_EXPIRE_MINUTES (Время жизни токена)
    EMAILHUNTER_API_KEY (Ключ от API hunter.io для верификации email)

### Устанока и запуск через docker-compose:

    docker-compose up --build

### Устанока и запуск без Докера:

Устанавливаем виртуальное окружение:  
    
    python -m virtualenv venv

Устанавливаем зависимости:  

    pip install -r requirements.txt

Запуск:  

    uvicorn main:app --reload

## Документация Swagger по API на эндпоинте /docs

