import re
from app.models.entities.user import userEntity
from app.models.repositories.user_repo import UserRepository



class UserService:

    @staticmethod
    def create_user(first_name, last_name, email, phone_number, address, password):
        user = UserRepository.get_users_by_email(email)
        if user:
            return True
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            return {"message": "Invalid email address!"}
        elif not re.match(r'[A-Za-z]+', first_name):
            return {"message": "Username must contain only characters!"}
        elif not first_name:
            return {"message": "Please enter your first name!"}
        elif not email:
            return {"message": "Please enter your email!"}
        
        else:
            user = userEntity(
                first_name = first_name,
                last_name = last_name,
                email = email,
                phone_number = phone_number,
                address = address,
                password = password
            )
        return UserRepository.save_user(user)
    

    @staticmethod
    def get_all_users():
        return UserRepository.get_all_users()
    

    @staticmethod
    def update_user(user_id, first_name=None, last_name=None, email=None, phone_number=None, address=None, password=None, role=None):
        user = UserRepository.update_user(user_id, first_name, last_name, email, phone_number, address, password, role) 
        return user.to_dict()