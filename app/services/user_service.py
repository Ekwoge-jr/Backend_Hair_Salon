from app.models.entities.user import userEntity
from app.models.repositories.user_repo import UserRepository
from app import bcrypt


class UserService:

    @staticmethod
    def create_user(full_name, email, phone_number, password=None):
        user = UserRepository.get_users_by_email(email)
        if user:
            return user
        
        if password is not None:
            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        else:
            hashed_password = None
        new_user = userEntity(
            full_name = full_name,
            email = email,
            phone_number = phone_number,    
            password = hashed_password
        )
        return UserRepository.save_user(new_user)
    

    def create_admin_or_stylist_user(full_name, email, phone_number, password):
        user = UserRepository.get_users_by_email(email)
        if user:
            return True
    
        user = userEntity(
            full_name = full_name,
            email = email,
            phone_number = phone_number,
            password = password,
        )
        return UserRepository.save_user(user)
    

    @staticmethod
    def get_all_users():
        return UserRepository.get_all_users()
    

    @staticmethod
    def update_user(user_id, full_name=None, email=None, phone_number=None, password=None, role=None):

        if password is not None:
            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        else:
            hashed_password = None
        user = UserRepository.update_user(user_id, full_name, email, phone_number, hashed_password, role) 
        return user