from app.models.entities.user import userEntity
from app.models.repositories.user_repo import UserRepository



class UserService:

    @staticmethod
    def create_user(first_name, last_name, email, phone_number, address, password):
        user = UserRepository.get_users_by_email(email)
        if user:
            return True
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
        user = UserRepository.get_users_by_id(user_id)
        if not user:
            return False
        
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if email:
            user.email = email
        if phone_number:
            user.phone_number = phone_number
        if address:
            user.address = address
        if password:
            user.password = password
        if role:
            user.role = role

        return UserRepository.update_user(user_id, user.first_name, user.last_name, user.email, user.phone_number, user.address, user.password, user.role)