from django.urls import path
from user_manager.views import create_user, delete_user, login_view, get_all_users, get_user_by_id, update_user_by_id, logout_view, create_admin
from inventory.views import (get_all_categories, create_category, get_category, update_category, delete_category, 
                             get_all_materials, create_material, get_material, update_material, delete_material)
from process.views import get_all_processes, create_process, update_process, delete_process, get_process
from order.views import (
    list_orders, create_order, retrieve_order, update_order, delete_order, 
    list_manager_orders, create_carpenter_request, get_order_creation_data, add_order_to_process, verification_process_list
    ,verification_process_view, verification_process_view_accept, complete_order, verification_process_view_reject
)
from django.conf import settings
from django.conf.urls.static import static
from carpenter_work.views import (list_carpenter_requests, carpenter_request_accept, carpenter_request_view,
                                   carpenter_request_respond, carpenter_request_respond, carpenter_request_update)
from process.views import list_process_details, get_process_details, accept_process_details, delete_process_details, add_to_process_verification, pause_process_details
from process.views import create_process_material, retrieve_process_material, delete_process_material, resume_process_details
from organization.views import get_organization, create_organization, update_organization, delete_organization, list_organizations

urlpatterns = [
    path('organizations/', create_organization, name='create_organization'),
    path('organizations/<int:organization_id>/', get_organization, name='get_organization'),
    path('organizations/list/', list_organizations, name='get_organization'),
    path('organizations/<int:organization_id>/update/', update_organization, name='update_organization'),
    path('organizations/<int:organization_id>/delete/', delete_organization, name='delete_organization'),

     #user and Login api's
     path('users/login/', login_view, name='login'),
     path('users/login/', logout_view, name='logout'),
     path('create-user/', create_user, name='create_user'),
     path('create-admin/', create_admin, name='create_admin'),
     path('users/delete/<int:user_id>/', delete_user, name='delete_user'),
     path('users/', get_all_users, name='get_all_user'),
     path('users/<int:user_id>/', get_user_by_id, name='get_user_by_id'),
     path('users/<int:user_id>/update/', update_user_by_id, name='update_user_by_id'),

     #inventory category api's
     path('categories/', get_all_categories, name='get_all_categories'),
     path('categories/create/', create_category, name='create_category'),
     path('categories/<int:pk>/', get_category, name='get_category'),
     path('categories/<int:pk>/update/', update_category, name='update_category'),
     path('categories/<int:pk>/delete/', delete_category, name='delete_category'),

     #inventory material api's
     path('materials/', get_all_materials, name='get_all_materials'),
     path('materials/create/', create_material, name='create_material'),
     path('materials/<int:pk>/', get_material, name='get_material'),
     path('materials/<int:pk>/update/', update_material, name='update_material'),
     path('materials/<int:pk>/delete/', delete_material, name='delete_material'),

     #processes api's
     path('processes/', get_all_processes, name='get_all_processes'),
     path('processes/create/', create_process, name='create_process'),
     path('processes/<int:pk>/', get_process, name='get_process'),
     path('processes/<int:pk>/update/', update_process, name='update_process'),
     path('processes/<int:pk>/delete/', delete_process, name='delete_process'),

    #order api's
     #------------ ADMIN API's-----------------------------------
    path('orders/create/', create_order, name='create_order'),
    path('orders/<int:pk>/update/', update_order, name='update_order'),
    path('orders/<int:pk>/delete/', delete_order, name='delete_order'),
    path('orders/status/<str:order_status>/', list_orders, name='list_orders'),
    path('orders/carpenter_request/<int:order_id>/', create_carpenter_request, name='create_carpenter_request'),
    path('orders/<int:order_id>/', retrieve_order, name='retrieve_order'),
    path('orders/<int:order_id>/completed/', complete_order, name='complete_order'),

    #--------------Manager API's---------------------------------
    #Add order to process
    path('orders/manager/add_to_process/', add_order_to_process, name='add_order_to_process'),
    #View Main manager order
    path('orders/manager/<int:order_id>/', retrieve_order, name='retrieve_order'),
    #List Main manager orders by status
    path('orders/manager/<str:order_status>/', list_manager_orders, name='list_manager_orders'),
    #Process completion verification list
    path('orders/manager/verification/list/', verification_process_list, name='verification_process_list'),
    #Process completion verification view
    path('orders/manager/<int:order_id>/verification/view/', verification_process_view, name='verification_process_view'), 
    #Process verification Accept
    path('orders/manager/<int:process_details_id>/verification/accept/', verification_process_view_accept, name='verification_process_view_accept'),    
   #Process verification Reject
    path('orders/manager/<int:process_details_id>/verification/reject/', verification_process_view_reject, name='verification_process_view_reject'),    

    #--------------Carpenter API's-------------------------------

    #List Carpenter Request
    path('carpenter_requests/', list_carpenter_requests, name='list_carpenter_requests'),
    #View Carpenter Request
    path('carpenter_requests/<int:order_id>/view/', carpenter_request_view, name='carpenter_request_view'),
    #Accept Carpenter Request
    path('carpenter_requests/<int:order_id>/accept/', carpenter_request_accept, name='carpenter_request_accept'),
    #Update Requested materials
    path('carpenter_requests/update/', carpenter_request_update, name='carpenter_request_update'),
    #Update Requested response
    path('carpenter_requests/<int:order_id>/respond/', carpenter_request_respond, name='carpenter_request_respond'),

    #--------------Process manager API's--------------------------

    #List Process manager Request
    path('process_details/list/', list_process_details, name='process-details-list'),
    #View Process Details Request
    path('process_details/<int:process_details_id>/view/', get_process_details, name='get-process-details'),
    #Accept Process Details Request
    path('process_details/<int:order_id>/accept/', accept_process_details, name='accept-process-details'),
    #Delete Process manager Request
    path('process_details/<int:process_details_id>/delete/', delete_process_details, name='process-details-delete'),
    #Add to process details verifications
    path('process_details/add_to_process_verification/<int:process_details_id>/', add_to_process_verification, name='add-to-process-verification'),
    #Add materials used in process
    path('process_materials/create/', create_process_material, name='create_process_material'),
    #Delete material used in process
    path('process_materials/<int:process_material_id>/delete/', delete_process_material, name='delete_process_material'),
    #Pause process
    path('process_details/<int:order_id>/pause/', pause_process_details, name='pause_process_details'),
    #Resume process
    path('process_details/<int:order_id>/resume/', resume_process_details, name='resume_process_details'),
    #Fetch data for order creation
    path('orders/creation-data/', get_order_creation_data, name='get_order_creation_data'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

