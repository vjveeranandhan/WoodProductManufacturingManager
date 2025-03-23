from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from .models import Process, ProcessMaterials, ProcessDetailsImage
from .ProcessSerializer import ProcessSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from process.process_details_serializer import ProcessDetailsSerializer
from process.models import ProcessDetails
from order.OrderSerializer import OrderSerializer
from order.models import Order
from user_manager.models import CustomUser
from user_manager.serializer import UserSerializer as ManagerSerializer
from user_manager.serializer import UserSerializer as WorksSerializer
from datetime import date, datetime
from .process_details_serializer import ProcessMaterialsSerializer
from django.shortcuts import get_object_or_404
from inventory.models import Material
from inventory.MaterialSerializer import MaterialSerializer
from .tests import user_admin_and_org_check, test_user_has_organization
from django.utils import timezone
from zoneinfo import ZoneInfo
from datetime import timedelta

# GET all processes
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_processes(request):
    try:
        user = request.user
        check_result, check_message = user_admin_and_org_check(user, request, message="get process")
        if not check_result:
            return Response({"message": check_message["message"]}, status=status.HTTP_403_FORBIDDEN)
        processes = Process.objects.filter(organization_id=user.organization_id.id).all()
        serializer = ProcessSerializer(processes, many=True)
        return Response(serializer.data)
    except:
        return Response({'message': 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)

# POST to create a new process
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_process(request):
    try:
        user = request.user
        check_result, check_message = user_admin_and_org_check(user, request, message="create process!")
        if not check_result:
            return Response({"message": check_message["message"]}, status=status.HTTP_403_FORBIDDEN)
        _data = request.data
        _data['organization_id'] = user.organization_id.id
        serializer = ProcessSerializer(data=_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({'message': 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)
    
# GET a specific process by ID
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_process(request, pk):
    try:
        user = request.user
        check_result, check_message = user_admin_and_org_check(user, request, message="get process!")
        if not check_result:
            return Response({"message": check_message["message"]}, status=status.HTTP_403_FORBIDDEN)
        process = Process.objects.filter(pk=pk, organization_id=user.organization_id.id).first()
        if process is None:
            return JsonResponse({'error': 'Process not found'}, status=404)
        serializer = ProcessSerializer(process)
        return Response(serializer.data)
    except Process.DoesNotExist:
        return Response({"error": "Process not found"}, status=status.HTTP_404_NOT_FOUND)

# PUT to update an existing process
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_process(request, pk):
    try:
        user = request.user
        check_result, check_message = user_admin_and_org_check(user, request, message="update process!")
        if not check_result:
            return Response({"message": check_message["message"]}, status=status.HTTP_403_FORBIDDEN)
        process = Process.objects.filter(pk=pk, organization_id=user.organization_id.id).first()
        if process is None:
            return JsonResponse({'error': 'Process not found'}, status=404)
        _data = request.data
        _data['organization_id'] = user.organization_id.id
        serializer = ProcessSerializer(process, data=_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Process.DoesNotExist:
        return Response({"error": "Process not found"}, status=status.HTTP_404_NOT_FOUND)

# DELETE a specific process by ID
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_process(request, pk):
    try:
        user = request.user
        check_result, check_message = user_admin_and_org_check(user, request, message="delete process!")
        if not check_result:
            return Response({"message": check_message["message"]}, status=status.HTTP_403_FORBIDDEN)
        process = Process.objects.filter(pk=pk, organization_id=user.organization_id.id).first()
        if process is None:
                return JsonResponse({'error': 'Process not found'}, status=404)
        process_details = ProcessDetails.objects.filter(process_id=process.id, organization_id=user.organization_id.id).first()
        if process_details:
            return Response({"message": "Cannot delete process with process details!"}, status=status.HTTP_400_BAD_REQUEST)
        process.delete()
        return Response({"message": "Process deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except Process.DoesNotExist:
        return Response({"error": "Process not found"}, status=status.HTTP_404_NOT_FOUND)

# ---------------------PROCESS DETAILS--------------------------------------------------------------    

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_process_details(request, process_details_id):
    try:
        process_details = ProcessDetails.objects.filter(id=process_details_id).first()
        if process_details is None:
                return JsonResponse({'error': 'Process Details not found'}, status=404)
        process_details.delete()
        return Response({"message": "Process details deleted successfully"}, status=status.HTTP_200_OK)
    except ProcessDetails.DoesNotExist:
        return Response({"error": "Process details not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# List process details request by manager
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_process_details(request):
    try:
        user = request.user
        # Filter ProcessDetails based on process_manager_id and process_id
        process_details = ProcessDetails.objects.filter(
            process_manager_id=user.id
        ).all()
        
        if not process_details.exists():
            return Response({"error": "No process details found"}, status=status.HTTP_404_NOT_FOUND)
        
        fields_to_remove = [
            # "id",
            # "product_name",
            # "product_name_mal",
            # "product_description",
            # "product_description_mal",
            "images",
            "product_length",
            "product_height",
            "product_width",
            "reference_image",
            "finish",
            "event",
            # "estimated_delivery_date",
            "estimated_price",
            "customer_name",
            "contact_number",
            "whatsapp_number",
            "email",
            "address",
            "carpenter_work_hr",
            "carpenter_work_cost",
            "carpenter_work_completion_date",
            "enquiry_status",
            "total_material_cost",
            "ongoing_expense",
            "order_stage_id",
            "main_manager_id",
            "carpenter_id",
            "material_ids",
            "carpenter_workers_id",
            "completed_processes",
            "material_cost",

        ]           
        list_data = []
        for detail in process_details:
            detail_data = {}
            # Get and serialize the related Order
            order = detail.order_id
            order_serializer = OrderSerializer(order)
            process_serializer = ProcessSerializer(detail.process_id)
            order_data = order_serializer.data
            for field in fields_to_remove:
                order_data.pop(field, None)
            detail_data['order_data'] = order_data
            detail_data['process_details'] = ProcessDetailsSerializer(detail).data
            detail_data['process']= process_serializer.data
            list_data.append(detail_data)
        
        return Response({'data': list_data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# API for PROCESS MANAGER to list all their process_details in a particular process and order
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_process_details(request, process_details_id):
    try:
        user = request.user
        process_details = ProcessDetails.objects.filter(
            id=process_details_id, process_manager_id = user.id, organization_id = user.organization_id.id
        ).first()
        if process_details is None:
            return Response({"error": "No process details found"}, status=status.HTTP_404_NOT_FOUND)
        order = Order.objects.filter(id=process_details.order_id.id).first()
        if order is None:
            return Response({"error": "Order found"}, status=status.HTTP_404_NOT_FOUND)
        order_fields_to_remove = [
            "estimated_price",
            "customer_name",
            "contact_number",
            "whatsapp_number",
            "email",
            "address",
            "carpenter_work_hr",
            "carpenter_work_cost",
            "carpenter_work_completion_date",
            "enquiry_status",
            "total_material_cost",
            "ongoing_expense",
            "carpenter_workers_id",
            "completed_processes",
            'material_cost',
            'current_process',
            'main_manager_id',
            'carpenter_id',
            # 'material_ids',
            'reference_image'
        ]           
        detail_data = {}

         # Get and serialize the related Order
        order_serializer = OrderSerializer(order)
        order_data = order_serializer.data
        for field in order_fields_to_remove:
            order_data.pop(field, None)
        detail_data['order_data'] = order_data
        
        main_manager_fields_to_remove=[
            'salary_per_hr',
            'age',
            'date_of_birth',
            'email'
        ]
         # Get and serialize the Main Manager
        main_manager = process_details.main_manager_id
        main_manager_serializer = ManagerSerializer(main_manager)
        main_manager_data = main_manager_serializer.data
        for field in main_manager_fields_to_remove:
            main_manager_data.pop(field, None)
        detail_data['main_manager'] = main_manager_data
        
        pro_manager_fields_to_remove=[
            'workers_salary',
            'material_price',
            'total_price',
            # 'process_id',
            'image',
            'order_id',
            'main_manager_id',
            'process_manager_id',
            'process_workers_id',
        ]
        #process
        detail_data['process'] = ProcessSerializer(process_details.process_id).data
        # Serialize ProcessDetails
        detail_serializer = ProcessDetailsSerializer(process_details)
        pro_details_data = detail_serializer.data
        for field in pro_manager_fields_to_remove:
            pro_details_data.pop(field, None)
        detail_data['process_details'] = pro_details_data
        
        # Get and serialize the Process Manager
        process_manager = process_details.process_manager_id
        process_manager_serializer = ManagerSerializer(process_manager)
        process_manager_serializer_data = process_manager_serializer.data
        for field in main_manager_fields_to_remove:
            process_manager_serializer_data.pop(field, None)
        detail_data['process_manager'] = process_manager_serializer_data

        workers_fields_to_remove=[
            'salary_per_hr',
            'age',
            'date_of_birth',
            'email'
        ]
        # Get and serialize the Process Workers
        process_workers = []
        for worker_id in detail_serializer.data['process_workers_id']:
            worker_data = CustomUser.objects.get(id=worker_id)
            worker_serializer = WorksSerializer(worker_data)
            worker_serializer_data = worker_serializer.data
            for field in workers_fields_to_remove:
                worker_serializer_data.pop(field, None)
            process_workers.append(worker_serializer_data)
        detail_data['workers_data'] = process_workers

         #Product Data
        product_data = {}
        if order.product:
            product_data = MaterialSerializer(order.product).data
        detail_data['product'] = product_data

        #process materials
        process_material_obj = ProcessMaterials.objects.filter(process_details_id=process_details.id).all()
        materials_used = []
        for material in process_material_obj:
            material_dict = {}  
            material_obj = Material.objects.filter(id = material.material_id.id).first()
            material_serialized = MaterialSerializer(material_obj)
            process_material_serialized = ProcessMaterialsSerializer(material)
            material_dict['material'] = material_serialized.data
            material_dict['material_used'] = process_material_serialized.data
            materials_used.append(material_dict)
        detail_data['used_materials'] = materials_used
        return Response({'data': detail_data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# API for PROCESS MANAGER to Accept their process_details in a particular process and order
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def accept_process_details(request, order_id):
    try:
        user = request.user
        order = Order.objects.filter(id=order_id, organization_id = user.organization_id.id).first()
        current_time = timezone.now()
        if not current_time:
            return Response({"error": 'unable to fetch time!'}, status=status.HTTP_400_BAD_REQUEST)
        if not order:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        process_details = ProcessDetails.objects.filter(
            order_id=order_id, process_id=order.current_process.id, process_manager_id = user.id, organization_id = user.organization_id.id).first()
        if not process_details:
            return Response ({'error': 'Process details not found'}, status=status.HTTP_404_NOT_FOUND)
        process_details.process_status = 'in_progress'
        process_details.request_accepted_date = current_time
        process_details.save()
        order.current_process_status = 'on_going'
        order.status = 'on_going'
        order.save()

        serializer = ProcessDetailsSerializer(process_details)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def pause_process_details(request, order_id):
    try:
        user = request.user
        order = Order.objects.filter(id=order_id, organization_id = user.organization_id.id).first()
        
        if not order:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        process_details = ProcessDetails.objects.filter(
            order_id=order_id, process_id=order.current_process.id, process_manager_id = user.id, organization_id = user.organization_id.id, 
            process_status = 'in_progress').first()
        if not process_details:
            return Response ({'error': 'Process details not found'}, status=status.HTTP_404_NOT_FOUND)
        
        current_time = timezone.now()
        if not current_time:
            return Response({"error": 'unable to fetch time!'}, status=status.HTTP_400_BAD_REQUEST)
        time_difference = 0
        if process_details.process_resume_date is None:
            time_difference = current_time - process_details.request_accepted_date
        else:
            time_difference = current_time - process_details.process_resume_date
        if time_difference == 0:
            return Response({"message": "No change"}, status=status.HTTP_200_OK)

        total_seconds = time_difference.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)

        print(f"Hours: {hours}, Minutes: {minutes}")

        # Alternative using timedelta components:
        hours_td = time_difference.days * 24 + time_difference.seconds // 3600
        minutes_td = (time_difference.seconds % 3600) // 60
        print(f"Hours (timedelta): {hours_td}, Minutes (timedelta): {minutes_td}")

        print(ProcessDetails.process_resume_date)
        time_delta_value = timedelta(hours=hours, minutes=minutes)
        process_details.working_hours += time_delta_value  # Add the duration\
        process_details.process_status = 'paused'
        process_details.save()
        order.current_process_status = 'paused'
        order.save()

        serializer = ProcessDetailsSerializer(process_details)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def resume_process_details(request, order_id):
    try:
        user = request.user
        order = Order.objects.filter(id=order_id, organization_id = user.organization_id.id).first()
        if not order:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        process_details = ProcessDetails.objects.filter(
            order_id=order_id, process_id=order.current_process.id, process_manager_id = user.id, organization_id = user.organization_id.id,
            process_status = 'paused').first()
        if not process_details:
            return Response ({'error': 'Process details not found'}, status=status.HTTP_404_NOT_FOUND)
        current_time = timezone.now()
        if not current_time:
            return Response({"error": 'unable to fetch time!'}, status=status.HTTP_400_BAD_REQUEST)
        process_details.process_resume_date = current_time
        process_details.process_status = 'in_progress'
        process_details.save()
        order.current_process_status = 'on_going'
        order.save()
        serializer = ProcessDetailsSerializer(process_details)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#------------------Process Materials API's-----------------------------------

# Create a new ProcessMaterial
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_process_material(request):
    try:
        data = request.data
        user = request.user
        material = get_object_or_404(Material, id=data['material_id'])
        if material.quantity < data['quantity']:
            return Response({"error": "Not enough material stock available."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update material price and calculate total price
        data['material_price'] = material.price
        data['total_price'] = material.price * data['quantity']

        process_details = ProcessDetails.objects.get(id=data['process_details_id'], process_manager_id = user.id, organization_id=user.organization_id.id)
        if not process_details:
            return Response({"error": "Process details not found!"}, status=status.HTTP_400_BAD_REQUEST)
        process_details_material_price = process_details.material_price
        process_details_material_price+= data['total_price']
        process_details.material_price = process_details_material_price

        process_details_total_price = process_details.total_price
        process_details_total_price+= data['total_price']
        process_details.total_price = process_details_total_price
        process_details.save()
        # Save the material quantity
        material.quantity -= data['quantity']
        material.save()
        
        order = Order.objects.filter(id=process_details.order_id.id).first()
        order_ongoing_expense = order.ongoing_expense
        order_ongoing_expense += data['total_price']
        order.ongoing_expense = order_ongoing_expense
        order.save()
        data['organization_id'] = user.organization_id.id
        serializer = ProcessMaterialsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Retrieve a specific ProcessMaterial by ID
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def retrieve_process_material(request, process_material_id):
    try:
        process_material = get_object_or_404(ProcessMaterials, id=process_material_id)
        serializer = ProcessMaterialsSerializer(process_material)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Delete a ProcessMaterial
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_process_material(request, process_material_id):
    try:
        process_material = get_object_or_404(ProcessMaterials, id=process_material_id)

        # Restore material stock on deletion
        material = process_material.material_id
        material.quantity += process_material.quantity
        material.save()

        material_total_price = (process_material.quantity)*(process_material.material_price)
        process_details = ProcessDetails.objects.filter(id=process_material.process_details_id.id).first()

        pd_total_price = process_details.total_price
        pd_material_price = process_details.material_price

        process_details.total_price = pd_total_price-material_total_price
        process_details.material_price = pd_material_price-material_total_price

        process_details.save()
        process_material.delete()
        return Response({"message": "Process material deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# Delete a ProcessMaterial
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def add_to_process_verification(request, process_details_id):
    try:
        user = request.user
        reference_images = request.FILES.getlist('image')

        # Fetch ProcessDetails with additional validation
        process_details = ProcessDetails.objects.filter(
            id=process_details_id, 
            process_manager_id=user.id, 
            organization_id=user.organization_id.id
        ).first()

        if not process_details:
            return Response({"error": "Process details not found"}, status=status.HTTP_404_NOT_FOUND)

        # Fetch Order with validation
        order = Order.objects.filter(
            id=process_details.order_id.id, 
            organization_id=user.organization_id.id
        ).first()

        if not order:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)


        current_time = timezone.now()
        if not current_time:
            return Response({"error": 'unable to fetch time!'}, status=status.HTTP_400_BAD_REQUEST)
        time_difference = 0
        if process_details.process_resume_date is None:
            time_difference = current_time - process_details.request_accepted_date
        else:
            time_difference = current_time - process_details.process_resume_date
        if time_difference == 0:
            return Response({"message": "No change!"}, status=status.HTTP_200_OK)

        if process_details.process_status == 'in_progress':
            total_seconds = time_difference.total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)

            print(f"Hours: {hours}, Minutes: {minutes}")

            # Alternative using timedelta components:
            hours_td = time_difference.days * 24 + time_difference.seconds // 3600
            minutes_td = (time_difference.seconds % 3600) // 60
            print(f"Hours (timedelta): {hours_td}, Minutes (timedelta): {minutes_td}")

            print(ProcessDetails.process_resume_date)
            time_delta_value = timedelta(hours=hours, minutes=minutes)
            process_details.working_hours += time_delta_value  # Add the duration\
        process_details.process_status = 'verification'
        order.current_process_status = 'verification'
        order.save()

        # Save images
        for image in reference_images:
            ProcessDetailsImage.objects.create(
                image=image,
                process_details=process_details  # Correct field name
            )

        process_details.save()

        return Response({"message": "Verification sent successfully"}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
