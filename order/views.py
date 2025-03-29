from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework import status
from datetime import date
from .models import Order, OrderImage, OrderAudio
from .OrderSerializer import OrderSerializer, OrderImageSerializer, OrderCreateSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from inventory.models import Material
from user_manager.models import CustomUser
from user_manager.serializer import UserSerializer, CustomUserSerializer, UserRetrieveSerializer
from django.http import JsonResponse
from carpenter_work.carpenter_enquire_serializer import CarpenterEnquireSerializer
from carpenter_work.models import CarpenterEnquire
from inventory.models import Material
from inventory.MaterialSerializer import MaterialSerializer
from process.models import ProcessDetails, ProcessMaterials
from process.models import Process
from process.ProcessSerializer import ProcessSerializer
from process.process_details_serializer import ProcessDetailsSerializer, ProcessMaterialsSerializer
from inventory.models import InventoryCategory, Material
from inventory.InventoryCategorySerializer import InventoryCategorySerializer
from inventory.MaterialSerializer import MaterialSerializer
from process.ProcessSerializer import ProcessSerializer
from user_manager.serializer import UserSerializer
from .tests import user_admin_and_org_check
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import datetime

# Create a new order
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    try:
        user = request.user
        check_result, check_message = user_admin_and_org_check(user, request, message="delete materials")
        if not check_result:
            return Response({"message": check_message["message"]}, status=status.HTTP_403_FORBIDDEN)
        data = request.data.copy()
        reference_images = request.FILES.getlist('reference_image')
        reference_audios = request.FILES.get('reference_audios')
        material_ids = request.data.getlist('material_ids')
        data.pop('reference_image', None)
        #Checking material_ids is belong to the user organization or not
        for material_id in material_ids:
            material_instance = Material.objects.filter(id=int(material_id)).first()
            if not material_instance or not material_instance.organization_id == user.organization_id:
                return Response({"message": "Material not found!"}, status=status.HTTP_403_FORBIDDEN)
        #Checking carpenter_id is belong to the user organization or not
        if data['carpenter_id']:
            carpenter_instance = CustomUser.objects.filter(id=int(data['carpenter_id'])).first()
            if not carpenter_instance or not carpenter_instance.organization_id == user.organization_id:
                return Response({"message": "Carpenter not found!"}, status=status.HTTP_403_FORBIDDEN)
        #Checking main_manager_id is belong to the user organization or not
        if data['main_manager_id']:
            main_manager_instance = CustomUser.objects.filter(id=int(data['main_manager_id'])).first()
            if not main_manager_instance or not main_manager_instance.organization_id == user.organization_id :
                return Response({"message": "Main Manager not found!"}, status=status.HTTP_403_FORBIDDEN)
        data['organization_id'] = user.organization_id.id
        serializer = OrderCreateSerializer(data=data)
        if serializer.is_valid():
            order_obj = serializer.save()
            for image in reference_images:
                OrderImage.objects.create(
                    image=image,
                    order=order_obj
                )
            if reference_audios:
                OrderAudio.objects.create(
                    audio=reference_audios,
                    order=order_obj
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=404)

# List all orders
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_orders(request, order_status):
    try:
        user = request.user
        check_result, check_message = user_admin_and_org_check(user, request, message="get orders!")
        if not check_result:
            return Response({"message": check_message["message"]}, status=status.HTTP_403_FORBIDDEN)
        orders = Order.objects.filter(status= order_status, organization_id=user.organization_id).order_by('-id').all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def retrieve_order(request, order_id):
    try:
        user = request.user
        check_result, check_message = user_admin_and_org_check(user, request, message="view orders!")
        if not check_result:
            return Response({"message": check_message["message"]}, status=status.HTTP_403_FORBIDDEN)
        order = Order.objects.filter(id=order_id, organization_id=user.organization_id).first()
        if not order:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        order_serializer = OrderSerializer(order)
        carpenter_enquiry = CarpenterEnquire.objects.filter(order_id=order.id).all()
        main_manager = CustomUser.objects.filter(id=order.main_manager_id.id).first()
        manager_serialized = UserSerializer(main_manager)
        carpenter = CustomUser.objects.filter(id=order.carpenter_id.id).first()
        carpenter_serialized = UserSerializer(carpenter)

        material_list = []
        material_ids = order_serializer.data['material_ids']
        for material_id in material_ids:
            material_data = Material.objects.get(id = material_id)
            serialized_material =  MaterialSerializer(material_data)
            material_list.append(serialized_material.data)

        carpenter_data = {}
        carpenter_data['carpenter_user'] = carpenter_serialized.data
        carpenter_data_list = []
        for carpenter_enquiry_item in carpenter_enquiry:
            carpenter_enquiry_serializer = CarpenterEnquireSerializer(carpenter_enquiry_item)
            carpenter_response = carpenter_enquiry_serializer.data
            carpenter_response['material'] = MaterialSerializer(carpenter_enquiry_item.material_id).data
            carpenter_data_list.append(carpenter_response)
        carpenter_data['carpenter_data']=carpenter_data_list
        
#------------------Completed Process Data-----------------------------------------------------
        completed_process_list = []
        completed_process_dict = {}
        materials_list = []
        if order.completed_processes:
            for completed_process in order.completed_processes.all():
                process_obj = Process.objects.filter(id = completed_process.id).first()
                process_serializer = ProcessSerializer(process_obj)
                completed_process_dict['completed_process'] = process_serializer.data
                process_details_obj =  ProcessDetails.objects.filter(order_id = order_id, process_id=process_serializer.data["id"]).first()
                process_details_serializer = ProcessDetailsSerializer(process_details_obj)
                completed_process_dict['completed_process_details'] = process_details_serializer.data
                #----- Material Data--------------------------
                process_materials_obj = ProcessMaterials.objects.filter(process_details_id = process_details_serializer.data['id']).all()
                material_dict = {}
                for material in process_materials_obj:
                    serialized_material = ProcessMaterialsSerializer(material)
                    materials_obj = Material.objects.filter(id=serialized_material.data['material_id']).first()
                    materials_obj_serializer = MaterialSerializer(materials_obj)
                    material_dict['completed_material_details']=materials_obj_serializer.data
                    material_dict['completed_material_used_in_process']=serialized_material.data
                    materials_list.append(material_dict)
                    material_dict={}
                completed_process_dict['materials_used'] = materials_list
                materials_list = []

                workers_list=[]
                for worker in process_details_obj.process_workers_id.all():
                    worker_obj = CustomUser.objects.get(id=worker.id)
                    worker_serialized = CustomUserSerializer(worker_obj)
                    workers_list.append(worker_serialized.data)
                process_manager_obj = CustomUser.objects.filter(id=process_details_obj.process_manager_id.id).first()
                process_manager_serialized = CustomUserSerializer(process_manager_obj)
                workers_list.append(process_manager_serialized.data)
                completed_process_dict['workers_data']=workers_list
                completed_process_list.append(completed_process_dict)
                completed_process_dict = {}
                workers_list=[]

#----------------Current Process Data---------------------------------------------------------------------------------
        current_process_dict = {}
        if order.current_process:
            current_process_obj=Process.objects.filter(id = order.current_process.id).first()
            current_process_serializer = ProcessSerializer(current_process_obj)
            current_process_dict['current_process'] = current_process_serializer.data
            process_details = ProcessDetails.objects.filter(order_id = order_id, process_id=order.current_process.id).first()
            current_process_material_list=[]
            if process_details:
                current_process_details_serializer = ProcessDetailsSerializer(process_details)
                current_process_dict['current_process_details'] = current_process_details_serializer.data
                current_process_materials_obj = ProcessMaterials.objects.filter(process_details_id = current_process_details_serializer.data['id']).all()
                current_process_material_dict = {}
                for material in current_process_materials_obj:
                    serialized_material = ProcessMaterialsSerializer(material)
                    materials_obj = Material.objects.filter(id=serialized_material.data['material_id']).first()
                    materials_obj_serializer = MaterialSerializer(materials_obj)
                    current_process_material_dict['current_material_details']=materials_obj_serializer.data
                    current_process_material_dict['current_material_used_in_process']=serialized_material.data
                    current_process_material_list.append(current_process_material_dict)
                    current_process_material_dict={}
                current_process_dict['current_process_materials_used'] = current_process_material_list
                
                workers_list=[]
                for worker in process_details.process_workers_id.all():
                    worker_obj = CustomUser.objects.get(id=worker.id)
                    worker_serialized = CustomUserSerializer(worker_obj)
                    workers_list.append(worker_serialized.data)
                process_manager_obj = CustomUser.objects.filter(id=process_details.process_manager_id.id).first()
                process_manager_serialized = CustomUserSerializer(process_manager_obj)
                workers_list.append(process_manager_serialized.data)
                current_process_dict['current_process_workers'] = workers_list
        #Order completion percentage calculation
        number_of_processes = Process.objects.count()
        completed_process = order.completed_processes.count()
        #Product Data
        product_data = {}
        if order.product:
            product_data = MaterialSerializer(order.product).data
        
        return Response({   'product': product_data,
                            'order_data': order_serializer.data,
                            'main_manager': manager_serialized.data,
                            'materials': material_list,
                            'carpenter_enquiry_data': carpenter_data,
                            'completed_process_data': completed_process_list,
                            'current_process': current_process_dict,
                            'completion_percentage': (completed_process/number_of_processes)*100
                        },
                        status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=404)

# Update an order
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_order(request, pk):
    try:
        user = request.user
        order = Order.objects.filter(pk=pk, organization_id=user.organization_id).first()
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    try:
        if order.status != 'initiated':
            return Response({'error': 'Can\'t edit the order'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            reference_images = request.FILES.getlist('reference_image')
            if reference_images:
                images = OrderImage.objects.filter(order= order.id)
                images.delete()
                for image in reference_images:
                    order_image = OrderImage.objects.create(
                        image = image,
                        order = order
                    )
                    order_image.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=404)

# Delete an order
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_order(request, pk):
    try:
        user = request.user
        check_result, check_message = user_admin_and_org_check(user, request, message="delete order")
        if not check_result:
            return Response({"message": check_message["message"]}, status=status.HTTP_403_FORBIDDEN)
        order = Order.objects.filter(pk=pk, organization_id=user.organization_id).first()
        if not order:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        if order.status != 'initiated':
            return Response({'error': 'Can\'t delete the order'}, status=status.HTTP_400_BAD_REQUEST)
        carpenter_enquiry = CarpenterEnquire.objects.filter(order_id=order.id, organization_id=user.organization_id).all()
        if carpenter_enquiry:
            carpenter_enquiry.delete()
        order.delete()
        return Response({'message': 'Order deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=404)

#----------------Carpenter Request------------------------------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_carpenter_request(request, order_id):
    try:
        user = request.user
        check_result, check_message = user_admin_and_org_check(user, request, message="send carpenter request!")
        if not check_result:
            return Response({"message": check_message["message"]}, status=status.HTTP_403_FORBIDDEN)
        order = Order.objects.filter(id= order_id, organization_id= user.organization_id).first()    
        if order is None:
            return JsonResponse({'error': 'Order not found'}, status=404)
        for material_id in order.material_ids.all():
            material_instance = Material.objects.filter(id=int(material_id.id), organization_id=user.organization_id).first()
            if material_instance is None:
                return JsonResponse({'error': 'Material not found!'}, status=404)
        for material_id in order.material_ids.all():
            material_instance = Material.objects.filter(id=int(material_id.id), organization_id=user.organization_id).first()
            carpenter_enq = CarpenterEnquire.objects.create(
                organization_id=user.organization_id,
                order_id=order,
                material_id=material_instance,
                carpenter_id=order.carpenter_id,
                status='requested'
            )
            carpenter_enq.save()
        order.enquiry_status = 'requested'
        order.save()
        return Response({'message': 'Success'}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=404)

#----------------Main Manager API's-----------------------------

# Retrieve manager order list
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_manager_orders(request, order_status):
    try:
        print("Hellooooooo")
        user = request.user
        orders = Order.objects.filter(main_manager_id=user.id, status=order_status, organization_id=user.organization_id).all()
        if not orders.exists():
            return Response(
                {"message": "No orders found for the given manager."}, 
                status=status.HTTP_200_OK
            )
        serializer = OrderSerializer(orders, many=True)
        for order in serializer.data:
            order.pop('images', None) 
            order.pop('estimated_price', None)
            order.pop('customer_name', None)
            order.pop('contact_number', None)
            order.pop('whatsapp_number', None)
            order.pop('email', None)
            order.pop('material_cost', None)
            order.pop('ongoing_expense', None)
            order.pop('main_manager_id', None)
            order.pop('material_ids', None)
            order.pop('carpenter_id', None)
            order.pop('current_process', None)
            order.pop('completed_processes', None)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=404)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_order_to_process(request):
    try:
        user = request.user
        data = request.data
        current_time = timezone.now()
        expected_completion_date_str = data['expected_completion_date']
        expected_completion_date = datetime.strptime(expected_completion_date_str, '%Y-%m-%d').date() #extract date portion.
        current_date = timezone.now().date() #extract date portion.
        if expected_completion_date < current_date:
            return JsonResponse({'error': 'Invalid date'}, status=400)
        if data.get('order_id'):
            order = Order.objects.filter(id = data['order_id'], organization_id = user.organization_id, main_manager_id=user.id).first()
            if order is None:
                return JsonResponse({'error': 'Order not found'}, status=400)
            if order.enquiry_status != 'completed':
                return JsonResponse({'error': 'Carpenter enquiry is not completed'}, status=404)
            if order.current_process_status != 'initiated' and order.current_process_status != 'completed':
                return JsonResponse({'error': 'Previous process is not completed'}, status=404)
            data['main_manager_id'] = order.main_manager_id.id
            data['organization_id'] = order.organization_id.id
        else:
            return JsonResponse({'error': 'Order not found'}, status=400)
        if 'process_id' in data:
            process = Process.objects.filter(id = data['process_id'], organization_id = user.organization_id).first()
            if process is None:
                return JsonResponse({'error': 'Process not found'}, status=400)
        else:
            return JsonResponse({'error': 'Process is not selected'}, status=400)
        
        if not data.get('process_manager_id'):
            return JsonResponse({'error': 'Process is not selected'}, status=400)
        else:
            process_manager = CustomUser.objects.filter(id = data['process_manager_id'], organization_id= user.organization_id).first()
            if process_manager is None:
                return JsonResponse({'error': 'Process manager not found'}, status=400)
        
        if not data.get('process_workers_id'):
            return JsonResponse({'error': 'Process is not selected'}, status=400)
        else:
            for worker in data['process_workers_id']:
                worker_user = CustomUser.objects.filter(id = worker, organization_id= user.organization_id).first()
                if worker_user is None:
                    return JsonResponse({'error': 'Invalid worker'}, status=400)
        if ProcessDetails.objects.filter(order_id = data['order_id'], process_id = data['process_id'], organization_id = user.organization_id).exists():
            return Response({"error": 'Order is already added to the process '}, status=status.HTTP_400_BAD_REQUEST)
        if not current_time:
            return Response({"error": 'unable to fetch time!'}, status=status.HTTP_400_BAD_REQUEST)
        _data = request.data
        _data['requested_date'] = current_time
        serializer = ProcessDetailsSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            order.current_process_status= 'requested'
            order.current_process = process
            order.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order_creation_data(request):
    """
    Get all necessary data for creating an order:
    - Categories
    - Materials
    - Processes
    - Managers
    """
    user = request.user
    try:
        # Get all active categories
        categories = InventoryCategory.objects.filter(organization_id=user.organization_id.id).order_by("id") .all()
        categories_data = InventoryCategorySerializer(categories, many=True).data

        # Get all active materials
        materials = Material.objects.filter(organization_id=user.organization_id.id).order_by("id") .all()
        materials_data = MaterialSerializer(materials, many=True).data

        # Get all active processes
        processes = Process.objects.filter(organization_id=user.organization_id.id).order_by("id") .all()
        processes_data = ProcessSerializer(processes, many=True).data

        # Get all managers
        users = CustomUser.objects.filter(organization_id=user.organization_id.id).order_by("id") .all()
        serializer = CustomUserSerializer(users, many=True)
        user_data = serializer.data

        response_data = {
            'categories': categories_data,
            'materials': materials_data,
            'processes': processes_data,
            'managers': user_data
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
#-------------------------------Main manager verification API's------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verification_process_list(request):
    try:
        user=request.user
        orders = Order.objects.filter(main_manager_id=user.id, current_process_status='verification', organization_id=user.organization_id.id).order_by('-id').all()
        if not orders.exists():
            return Response(
                {"message": "No orders found for the given managers."}, 
                status=status.HTTP_200_OK
            )
        serializer = OrderSerializer(orders, many=True)
        for order in serializer.data:
            order.pop('images', None) 
            order.pop('estimated_price', None)
            order.pop('customer_name', None)
            order.pop('contact_number', None)
            order.pop('whatsapp_number', None)
            order.pop('email', None)
            order.pop('material_cost', None)
            order.pop('ongoing_expense', None)
            order.pop('main_manager_id', None)
            order.pop('material_ids', None)
            order.pop('carpenter_id', None)
            order.pop('completed_processes', None)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verification_process_view(request, order_id):
    try:
        orders = Order.objects.filter(id=order_id).first()
        if not orders:
            return Response(
                {"message": "No orders found for the given managerss."}, 
                status=status.HTTP_200_OK
            )
        serializer = OrderSerializer(orders)
        order=serializer.data
        order.pop('estimated_price', None)
        order.pop('customer_name', None)
        order.pop('contact_number', None)
        order.pop('whatsapp_number', None)
        order.pop('email', None)
        order.pop('material_cost', None)
        order.pop('ongoing_expense', None)
        order.pop('main_manager_id', None)
        order.pop('material_ids', None)
        order.pop('carpenter_id', None)

        process = Process.objects.filter(id=orders.current_process.id).first()
        process_details = ProcessDetails.objects.filter(order_id = orders.id,process_id=orders.current_process.id).first()
        process_materials = ProcessMaterials.objects.filter(process_details_id= process_details.id).all()

        process_serializer =ProcessSerializer(process)
        process_details_serializer = ProcessDetailsSerializer(process_details)
        process_materials_serializer = ProcessMaterialsSerializer(process_materials, many=True)
        material_data = {}
        material_list = []
        for material in process_materials_serializer.data:
            material_obj = Material.objects.filter(id = material['material_id']).first()
            material_serializer = MaterialSerializer(material_obj)
            material_data=material
            material_data['material']=material_serializer.data
            material_list.append(material_data)
        #Product Data
        product_data = {}
        if orders.product:
            product_data = MaterialSerializer(orders.product).data
        return Response({'data':{
            'product': product_data,
            'order_data': order,
            'process': process_serializer.data,
            'process_details': process_details_serializer.data,
            'materials': material_list
        }}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Accept the completion request of a process
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def verification_process_view_accept(request, process_details_id):
    try:
        user = request.user
        process_details_obj = ProcessDetails.objects.filter(id= process_details_id, organization_id=user.organization_id.id,process_status='verification').first()
        if not process_details_obj:
            return Response(
                {"message": "Process Details not found."}, 
                status=status.HTTP_200_OK
            )
        order_obj = Order.objects.filter(id=process_details_obj.order_id.id, main_manager_id=user.id ,organization_id=user.organization_id.id).first()
        if not order_obj:
            return Response(
                {"message": "Order not found."}, 
                status=status.HTTP_200_OK
            )
        completion_date = date.today()
        total_seconds = process_details_obj.working_hours.total_seconds()
        total_working_hrs = round(total_seconds / 3600)
        print("total_working_hrs ", total_working_hrs)
        work_expense = 0
        for workers in process_details_obj.process_workers_id.all():
            worker_obj = CustomUser.objects.filter(id=workers.id).first()
            worker_serializer = CustomUserSerializer(worker_obj)
            user_data = worker_serializer.data
            work_expense += user_data['salary_per_hr'] * total_working_hrs

        process_manager_id = CustomUser.objects.filter(id=process_details_obj.process_manager_id.id).first()
        process_manager_serializer = CustomUserSerializer(process_manager_id)
        process_manager_data = process_manager_serializer.data
        work_expense += process_manager_data['salary_per_hr'] * total_working_hrs

        process_details_total_price = 0
        process_details_obj.workers_salary = work_expense
        process_details_total_price = process_details_obj.total_price
        process_details_obj.total_price = work_expense + process_details_total_price
        process_details_obj.process_status = 'completed'
        process_details_obj.completion_date = completion_date
        process_details_obj.save()

        order_obj = Order.objects.filter(id=process_details_obj.order_id.id).first()
        order_obj.current_process_status = 'completed'
        on_going_expense = order_obj.ongoing_expense
        on_going_expense+=work_expense
        order_obj.ongoing_expense = on_going_expense
        order_obj.completed_processes.add(process_details_obj.process_id)
        order_obj.save()
        return Response({'data':{"Success"}}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def verification_process_view_reject(request, process_details_id):
    try:
        process_details_obj = ProcessDetails.objects.filter(id= process_details_id).first()
        if not process_details_obj:
            return Response(
                {"message": "Process Details not found."}, 
                status=status.HTTP_200_OK
            )
        if process_details_obj.process_status != 'verification':
            return Response(
                {"message": "Process Details not available for verification"}, 
                status=status.HTTP_200_OK
            )
        process_details_obj.process_status = 'in_progress'
        process_details_obj.save()
        return Response({'data':{"Success"}}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def complete_order(request, order_id):
    try:
        order = Order.objects.filter(id=order_id).first()
        if order.current_process_status != 'completed':
            return Response({'error': 'Current process is not completed!'}, status=status.HTTP_400_BAD_REQUEST)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    try:
        order.status = 'completed'
        order.save()
        return Response({'data': 'Order completed'}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=404)