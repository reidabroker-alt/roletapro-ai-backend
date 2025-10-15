from app.main import app

# FastAPI é uma aplicação ASGI, não WSGI diretamente.
# Para implantar com Gunicorn (que pode servir ASGI com workers Uvicorn),
# não precisamos de um wrapper WSGI tradicional. O Gunicorn pode chamar o Uvicorn.
# No entanto, se a ferramenta de deploy espera um arquivo WSGI, podemos criar um dummy.
# A melhor abordagem é configurar o Gunicorn para usar o Uvicorn workers.
# Para fins de compatibilidade com a ferramenta de deploy que espera Flask/WSGI,
# vamos criar um placeholder. A implantação real precisará de Gunicorn com Uvicorn workers.

# Se a ferramenta de deploy tentar importar 'application' ou 'app' de wsgi.py,
# podemos retornar a instância do FastAPI diretamente, embora não seja WSGI.
# A ferramenta de deploy pode ter sua própria maneira de iniciar o servidor.

# Para fins de compatibilidade com o deploy_backend que espera Flask, 
# vamos tentar um wrapper mínimo, embora não seja o ideal para FastAPI.
# Isso é um hack para tentar enganar a ferramenta de deploy.

# from flask import Flask
# flask_app = Flask(__name__)

# @flask_app.route('/')
# def hello():
#     return 'Hello from Flask wrapper for FastAPI!'

# application = flask_app

# A abordagem mais correta para FastAPI com Gunicorn é:
# gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app

# Como o `deploy_backend` espera Flask, vamos tentar um Flask dummy app.
# Se isso não funcionar, teremos que reconsiderar a estratégia de deploy.

from flask import Flask

flask_app = Flask(__name__)

@flask_app.route('/')
def hello():
    return 'Hello from Flask wrapper for FastAPI!'

application = flask_app

