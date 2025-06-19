import sys
import os

# Ajout du répertoire parent au path système
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.templating import Jinja2Templates
import uvicorn
from dash_app.app import app as app_dash  # Assure-toi que dash_app/app.py existe
import requests

app = FastAPI()

# Répertoires corrigés (templates et static sont dans fastapi_app/)
base_dir = os.path.dirname(__file__)
templates_dir = os.path.join(base_dir, "fastapi_app", "templates")
static_dir = os.path.join(base_dir, "fastapi_app", "static")

# Montage des fichiers statiques et des templates
app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# Utilisateur de test
user = {"admin": "123"}

# URL API météo
EXTERNAL_API_URL = 'https://wetather-api-hdevfbcpdga0brcm.canadaeast-01.azurewebsites.net/info'

# Fonction pour récupérer les infos météo depuis une API locale
def get_external_info():
    try:
        response = requests.get(EXTERNAL_API_URL)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Erreur {response.status_code} lors de l'appel à l'API"}
    except Exception as e:
        return {"error": f"Exception levée : {str(e)}"}

# Route d’accueil
#@app.get("/", response_class=HTMLResponse)
#async def home_page(request: Request):
    #return templates.TemplateResponse("home.html", {
        #"request": request,
        #"message": "Bienvenue sur ma page home de l’API FastAPI"
    #})

@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    weather_info = get_external_info()

    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "Bienvenue sur ma page home de l’API FastAPI",
        "weather": weather_info
    })

# Page de login (GET)
@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": None
    })

# Traitement du formulaire de login (POST)
@app.post("/login", response_class=HTMLResponse)
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    if username in user and user[username] == password:
        return RedirectResponse(url="/dashboard", status_code=302)
    else:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Identifiants incorrects"
        })

# Intégration de l'application Dash
app.mount("/dashboard", WSGIMiddleware(app_dash.server))

# Lancer avec : uvicorn main1:app --reload
