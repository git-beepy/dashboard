import sys
import os

# Adiciona o diretório pai ao sys.path para que o Python possa encontrar o módulo 'main'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from main import app

if __name__ == "__main__":
    app.run()


