from flask_restful import Resource, reqparse
from models.hotel import HotelModel
from flask_jwt_extended import jwt_required
import sqlite3
from resources.filters import normalize_path_params,consulta_com_cidade,consulta_sem_cidade
from models.site import SiteModel

#path /hoteis?Cidade=Rio de Janeiro&estrelas_min=4&diaria_max=400

path_params = reqparse.RequestParser()
path_params.add_argument('estrelas_min', type=float, default=0, location='args')
path_params.add_argument('estrelas_max', type=float, default=5, location='args')
path_params.add_argument('diaria_min', type=float, default=0, location='args')
path_params.add_argument('diaria_max', type=float, default=10000, location='args')
path_params.add_argument('cidade', type=str, default=None, location='args')
path_params.add_argument('limit', type=float, default=50, location='args')
path_params.add_argument('offset', type=float, default=0, location='args')




class Hoteis(Resource):
    def get(self):
        connection= sqlite3.connect('./instance/banco.db') # Ficar atendo aos caminhos do banco
        cursor=connection.cursor()

        dados = path_params.parse_args()
        dados_validos = {chave:dados[chave] for chave in dados if dados[chave] is not None}
        parametros = normalize_path_params(**dados_validos)

        if not parametros.get('cidade'):
            tupla = (
                parametros['estrelas_min'],
                parametros['estrelas_max'],
                parametros['diaria_min'],
                parametros['diaria_max'],
                parametros['limit'],
                parametros['offset']
            )
            resultado = cursor.execute(consulta_sem_cidade, tupla)

        else:
            tupla = (
                parametros['estrelas_min'],
                parametros['estrelas_max'],
                parametros['diaria_min'],
                parametros['diaria_max'],
                parametros['cidade'],
                parametros['limit'],
                parametros['offset']
            )
            resultado = cursor.execute(consulta_com_cidade, tupla)

        hoteis = [] 
        for linha in resultado:
            hoteis.append({
            'hotel_id':linha[0],
            'nome':linha[1],
            'estrelas': linha[2],
            'diaria':linha[3],
            'cidade':linha[4],
            'site_id':linha[5],

            })

        
        return {'hoteis': hoteis}

class Hotel (Resource):
    argumentos = reqparse.RequestParser()
    argumentos.add_argument('nome', type = str , required=True , help='The field "nome" cannot be left blank')
    argumentos.add_argument('estrelas', type = float , required= True , help ='The field "estrelas" cannot be left blank')
    argumentos.add_argument('cidade',)
    argumentos.add_argument('diaria',)    
    argumentos.add_argument('site_id',type=int,required = True, help = "Every hotel needs to to be linked with a site")

    def get(self,hotel_id):   
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel :
            return hotel.json()
        return {'message' : 'Hotel not found'}, 404 # NOT FOUND
    
    @jwt_required()
    def post(self,hotel_id):
        if HotelModel.find_hotel(hotel_id):
            return {'message' : "Hotel id '{}' already exists.".format(hotel_id)},400 # Bad request 
        
        dados = Hotel.argumentos.parse_args()    
        hotel = HotelModel (hotel_id,**dados)

        if not SiteModel.find_by_id(dados.get('site_id')):
            return {'message':'The hotel must be associated to a valid site ID'},400

        try:
            hotel.save_hotel()
        except:
            return {'message':'An internal error ocurred trying to save hotel'},500 # Internal Server error    
        return hotel.json(),201
    
    @jwt_required()
    def put(self,hotel_id):
        dados = Hotel.argumentos.parse_args()
        hotel_encontrado = HotelModel.find_hotel(hotel_id)

        if hotel_encontrado:
            hotel_encontrado.update_hotel(**dados)
            hotel_encontrado.save_hotel()
            return hotel_encontrado.json(), 200
        hotel = HotelModel(hotel_id,**dados)  
        try:
            hotel.save_hotel()
        except:
            return {'message':'An internal error ocurred trying to save hotel'},500 # Internal Server error
        return hotel.json(), 201 # Created a new hotel

    @jwt_required()
    def delete(self,hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            try:
                hotel.delete_hotel()
            except:
                return {'message':'An internal error ocurred trying to save hotel'},500 # Internal Server error
            
            return {'message':'Hotel deleted'},200
        return {'message' :'Hotel not found'},404