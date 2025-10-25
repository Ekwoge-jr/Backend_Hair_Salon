from sqlalchemy.orm import Session
from app import db
from app.models.orm.user_model import UserModel
from app.models.entities.user import userEntity

class UserRepository:


# conversion
    @staticmethod
    def _to_entity(model: UserModel):
        """Convert ORM model to Entity."""
        return userEntity(
            id = model.id,
            first_name = model.first_name,
            last_name = model.last_name,
            email = model.email,
            phone_number = model.phone_number,
            address = model.address,
            password = model.password,
            role = model.role
        )


# create
    @staticmethod
    def save_user(entity: userEntity):
        new_user = UserModel(
            first_name = entity.first_name,
            last_name = entity.last_name,
            email = entity.email,
            phone_number = entity.phone_number,
            address = entity.address,
            password = entity.password
        )
        db.session.add(new_user)
        db.session.commit()
        db.session.refresh(new_user)

        # Return the entity with ID set
        entity.id = new_user.id
        return entity
    

# read
    @staticmethod
    def get_all_users():
        results = db.session.query(UserModel).all()
        return [UserRepository._to_entity(user) for user in results]
    
    @staticmethod
    def get_users_by_id(user_id):
        result = db.session.query(UserModel).filter(UserModel.id == user_id).first()
        return UserRepository._to_entity(result) if result else None
    
    @staticmethod
    def get_users_by_email(email):
        result = db.session.query(UserModel).filter(UserModel.email == email).first()
        return UserRepository._to_entity(result) if result else None
    

# update
    @staticmethod
    def update_user(user_id, first_name=None, last_name=None, email=None, phone_number=None, address=None, password=None, role=None):
        user = db.session.query(UserModel).filter_by(id=user_id).first()
        if user:
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.phone_number = phone_number
            user.address = address
            user.password = password
            user.role = role
            db.session.commit()
            db.session.refresh(user)
            return True
        return False


# delete
    @staticmethod
    def delete_user(user_id):
        user = db.session.query(UserModel).filter_by(id=user_id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False