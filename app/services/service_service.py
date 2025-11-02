from app.models.repositories.service_repo import ServiceRepository
from app.models.entities.service import serviceEntity


class ServiceService:

    @staticmethod
    def create_service(name, description, price, duration):
        service = serviceEntity(
            name = name,
            description = description,
            price = price,
            duration = duration
        )
        return ServiceRepository.save_service(service)
    

    @staticmethod
    def get_all_services():
        return ServiceRepository.get_all_services()
    

    @staticmethod
    def update_service(service_id, name=None, description=None, price=None, duration=None):    
        service = ServiceRepository.update_service(service_id, name, description, price, duration)
        return service.to_dict()
    

    @staticmethod
    def delete_service(service_id):
        return ServiceRepository.delete_service(service_id)
        