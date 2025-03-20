from django.test import TestCase

# Check if the user is an admin
def test_user_is_admin(user):
    if user.isAdmin == False:
            return False
    else:
        return True
    
def test_user_has_organization(user):
    if user.organization_id is None:
        return False
    else:
        return True