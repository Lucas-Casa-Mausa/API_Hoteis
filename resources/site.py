from flask_restful import Resource
from models.site import SiteModel

class Sites(Resource):
    def get(self):
        return {'sites': [site.json() for site in SiteModel.query.all()]}
    
class Site(Resource):
    def get(self,url):
        site = SiteModel.find_site(url)
        if site:
            return site.json()
        return {'message' : 'Site not found'}, 404 # NOT FOUND

    def post(self,url):
        if SiteModel.find_site(url):
            return {'message': "The site '{}' already exists".format(url)},400
        site = SiteModel(url)  
        try:
            site.save_site()
        except:
            return {'message' : 'An internal error has ocurred trying to create a new site'},500
        return site.json()
    
    def delete(self,url):
        site = SiteModel.find_site(url)
        if site:
            try:
                site.delete_site()
            except:
                return {'message':"Site was not found"},404
            return {'message': "Site was delete sucessfully"},200
        
    

