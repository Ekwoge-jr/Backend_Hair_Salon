from app.models.repositories.service_repo import ServiceRepository
from app.models.entities.service import serviceEntity


class ServiceService:

    @staticmethod
    def create_service(name, description, price, image, duration):
        service = serviceEntity(
            name = name,
            description = description,
            price = price,
            image = image,
            duration = duration
        )
        return ServiceRepository.save_service(service)
    

    @staticmethod
    def get_all_services():
        return ServiceRepository.get_all_services()
    

    @staticmethod
    def update_service(service_id, name=None, description=None, price=None, image=None, duration=None):    
        service = ServiceRepository.update_service(service_id, name, description, price, image, duration)
        return service
    

    @staticmethod
    def delete_service(service_id):
        return ServiceRepository.delete_service(service_id)
        