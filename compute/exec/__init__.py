from flask import Blueprint

exec_blueprint = Blueprint('exec', __name__)
from .exec_bridgar import *