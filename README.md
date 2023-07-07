## Установка:

Клонируем проект:  

    git clone https://github.com/anza-afk/fastapi_test_task.git  

Устанавливаем виртуальное окружение:  
    
    python -m virtualenv venv

Устанавливаем зависимости:  

    pip install -r requirements.txt

    
Тут необходимо создать .env файл с переменными:

    SECRET_KEY (Сгенерированный "openssl rand -hex 32" секретный ключ)
    ALGORITHM (Алгоритм шифрования токена)
    ACCESS_TOKEN_EXPIRE_MINUTES (Время жизни токена)
    EMAILHUNTER_API_KEY (Ключ от API hunter.io для верификации email)

как в файле с примером .env_example  

## Запуск:  

uvicorn main:app --reload

 
## Документация Swagger по API на /docs

