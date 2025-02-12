from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
import secrets
from blacklist import BLACKLIST
from resources.hotel import Hoteis, Hotel
from resources.usuario import User, UserConfirm, UserRegister, UserLogin, UserLogout
from sql_Alchemy import banco  
from resources.site import Site,Sites

# Gerando uma chave secreta segura para JWT
secret_key = secrets.token_hex(32)


app = Flask(__name__)

# Configurações do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False        
app.config['JWT_SECRET_KEY'] = secret_key   # Configuração do JWT
app.config['JWT_BLACKLIST_ENABLED'] = True

# Inicializando os componentes do Flask
banco.init_app(app)  
api = Api(app)
jwt = JWTManager(app)

@jwt.token_in_blocklist_loader
def verifica_blacklist(jwt_header, jwt_payload):
    return jwt_payload['jti'] in BLACKLIST


@jwt.revoked_token_loader
def token_acesso_invalidado():
    return jsonify({'message': 'You have been logged out'}), 401


# Adicionando recursos à API
api.add_resource(Hoteis, '/hoteis') 
api.add_resource(Hotel, '/hoteis/<string:hotel_id>')
api.add_resource(User, '/usuarios/<int:user_id>')
api.add_resource(UserRegister, '/cadastro')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')
api.add_resource(Sites,'/sites')
api.add_resource(Site, '/sites/<string:url>')
api.add_resource(UserConfirm,'/confirmacao/<int:user_id>')

if __name__ == '__main__':
    with app.app_context():
        banco.create_all() 
    app.run(debug=True)



