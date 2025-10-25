from app.models.orm.service_model import ServiceModel
from sqlalchemy.orm import Session
from app import db
from app.models.entities.service import serviceEntity

class ServiceRepository:


# conversion
    @staticmethod
    def _to_entity(model: ServiceModel):
        """Convert ORM model to Entity."""
        return serviceEntity(
            id = model.id,
            name = model.name,
            description = model.description,
            price = model.price,
            duration = model.duration
        )


# create
    @staticmethod
    def save_service(entity: serviceEntity):
        new_service = ServiceModel(
            name = entity.name,
            description = entity.description,
            price = entity.price,
            duration = entity.duration
        )
        db.session.add(new_service)
        db.session.commit()
        db.session.refresh(new_service)

        # Return the entity with ID set
        entity.id = new_service.id
        return entity


# read
    @staticmethod
    def get_all_services():
        results = db.session.query(ServiceModel).all()
        return [ServiceRepository._to_entity(service) for service in results]
    
    @staticmethod
    def get_service_by_id(service_id: int):
        result = db.session.query(ServiceModel).filter(ServiceModel.id == service_id).first()
        return ServiceRepository._to_entity(result) if result else None
    
    @staticmethod
    def get_service_by_name(name):
        results = db.session.query(ServiceModel).filter(ServiceModel.name == name).all()
        return [ServiceRepository._to_entity(service) for service in results]


# update
    @staticmethod
    def update_service(service_id, name, description, price, duration):
        service = db.session.query(ServiceModel).filter_by(id=service_id).first()
        if service:
            service.name = name
            service.description = description
            service.price = price
            service.duration = duration
            db.session.commit()
            db.session.refresh(service)
            return True
        return False
    

# delete
    @staticmethod
    def delete_service(service_id):
        service = db.session.query(ServiceModel).filter_by(id=service_id).first()
        if service:
            db.session.delete(service)
            db.session.commit()
            return True
        return False
    



"""
class ServiceRepository:
    def __init__(self, db: Session):
        self.db = db       # self = the current instance, holds the db session


# create
    def save_service(self, name, description, price, duration):
        new_service = ServiceModel(
            name = name,
            description = description,
            price = price,
            duration = duration
        )
        self.db.add(new_service)
        self.db.commit()
        self.db.refresh(new_service)
        return new_service


# read
    def get_all_services(self):
        return self.db.query(ServiceModel).all()

    def get_service_by_id(self, service_id: int):
        return self.db.query(ServiceModel).filter(ServiceModel.id == service_id).first()


# update
    def update_service(self, service_id, name, description, price, duration):
        service = self.get_service_by_id(service_id)
        if service:
            service.name = name
            service.description = description
            service.price = price
            service.duration = duration
            self.db.commit()
            self.db.refresh(service)
        return service
    

# delete
    def delete_service(self, service_id):
        service = self.get_service_by_id(service_id)
        if service:
            self.db.delete(service)
            self.db.commit()
        return service
"""