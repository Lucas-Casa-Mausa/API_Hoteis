from sql_Alchemy import banco
from flask import request,url_for
from requests import post
from dotenv import load_dotenv
import os


MAILGUN_API_KEY = 'MAILGUN_API_KEY'
MAILGUN_DOMAIN = 'MAILGUN_DOMAIN'
FROM_TITLE = 'FROM_TITLE'
FROM_EMAIL = 'FROM_EMAIL'


class UserModel(banco.Model):
    __tablename__ = 'usuarios'

    user_id = banco.Column(banco.Integer, primary_key = True)
    login = banco.Column(banco.String(40),nullable = False, unique= True)
    senha = banco.Column(banco.String(40))
    email = banco.Column(banco.String(80),nullable = False, unique= True)
    ativado = banco.Column(banco.Boolean, default = False)
    
    def __init__(self,login,senha,ativado,email):
        self.login = login
        self.senha = senha
        self.ativado = ativado
        self.email = email  

    def send_confirmation_email(self):
        #/confirmacao/{user_id}
        #'http://127.0.0.1:5000/'
        link = request.url_root[:-1] + url_for('userconfirm',user_id = self.user_id)
        return post('https://api.mailgun.net/v3/{}/messages'.format(MAILGUN_DOMAIN ),
                    auth=('api',MAILGUN_API_KEY),
                    data={'from':'{} <{}>'.format(FROM_TITLE,FROM_EMAIL),
                        'to': self.email,
                        'subject':'Confirmação de Cadastro',
                        'text' :'Confirme seu cadastro clicando no link a seguir: {}'.format(link),   
                        'html': '<html><p>Confirme seu cadastro clicando no link a seguir: <a href="{}">CONFIRMAR EMAIL</a></p></html>'.format(link)
                        }
                    )
        

    def json(self):
        return {
            'user_id': self.user_id,
            'login' : self.login,
            'ativado' : self.ativado,
            'email':self.email
            }
    
    @classmethod
    def find_user(cls,user_id):
        user = cls.query.filter_by(user_id=user_id).first() 
        if user:
            return user
        return None
    
    @classmethod
    def find_by_login(cls,login):
        login = cls.query.filter_by(login=login).first() 
        if login:
            return login
        return None

    def save_user(self):
        banco.session.add(self)
        banco.session.commit()


    def delete_user(self):
        banco.session.delete(self)
        banco.session.commit()

    @classmethod
    def find_by_email(cls,email):
        user = cls.query.filter_by(email=email).first() 
        if user:
            return user
        return None
    