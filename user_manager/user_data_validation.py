import re
from .models import CustomUser

def validate_user_data(data, activity):
    phone_number_pattern = r'^[6-9]\d{9}$'
    phone_number_regex = re.compile(phone_number_pattern)
    try:
        
        if 'phone' in data:
            if data['phone'] is not None:
                if activity == 'user-update':
                    if phone_number_regex.match(data['phone']):
                        if CustomUser.objects.filter(phone= data['phone']).exists():
                            return False, "Phone number alrady exists!"
                    else:
                        return False, "Invalid phone number!"
                else:
                    if CustomUser.objects.filter(phone= data['phone']).exists():
                        return False, "Phone number alrady exists!"
            else:
                return False, "Phone Number should not be Null!"
        if 'email' in data:
            if data['email'] is not None:
                if CustomUser.objects.filter(email= data['email'] ).exists():
                    return False, "Email alrady exists!"
            else:
                return False, "Email should not be Null!"
        else:
            return False, "Email is missing!"
        if 'password' in data:
            if data['password'] is None:
                return False, "Password should not be Null!"
        else:
            return False, "Password field is missing!"
        if 'isAdmin' in data:
            if data['isAdmin'] is None:
                return False, "isAdmin should not be Null!"
        else:
            return False, "isAdmin field is missing!"
        return True, "Valid."
    except:
        return False, "Something went wrong. Please Try agan later."