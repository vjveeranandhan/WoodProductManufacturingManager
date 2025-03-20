# Create your tests here.
def test_user_is_admin_or_enq_tkr(user):
    if user.isAdmin == False and user.enq_taker == False:
        return False
    else:
        return True
    
def test_user_has_organization(user):
    if user.organization_id is None:
        return False
    else:
        return True
    
def user_admin_and_org_check(user,request, message):
    user = request.user
    if test_user_is_admin_or_enq_tkr(user) == False:
        return False,{"message": f"You don't have permission {message}!"}
    if test_user_has_organization(user) == False:
                return False,{"message": "Organization registration is not completed!"}
    return True, {"message": "Success"}