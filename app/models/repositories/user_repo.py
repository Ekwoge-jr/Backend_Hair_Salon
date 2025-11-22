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
            full_name = model.full_name,
            email = model.email,
            phone_number = model.phone_number,
            password = model.password,
            role = model.role
        )


# create
    @staticmethod
    def save_user(entity: userEntity):
        new_user = UserModel(
            full_name = entity.full_name,
            email = entity.email,
            phone_number = entity.phone_number,
            password = entity.password,
            role = entity.role
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
    def update_user(user_id, full_name=None, email=None, phone_number=None, password=None, role=None):
        
        try:
            user = db.session.query(UserModel).filter_by(id=user_id).first()
            if not user:
                return {"error": "Service not available"}
        
            if full_name is not None:
                user.first_name = full_name
            if email is not None:
                user.email = email
            if phone_number is not None:
                user.phone_number = phone_number
            if password is not None:
                user.password = password
            if role is not None:
                user.role = role

            db.session.commit()
            db.session.refresh(user)
            return UserRepository._to_entity(user)
        
        except Exception as e:
            db.session.rollback()
            return {"error": f"Failed to update user: {str(e)}"}


# delete
    @staticmethod
    def delete_user(user_id):
        user = db.session.query(UserModel).filter_by(id=user_id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False