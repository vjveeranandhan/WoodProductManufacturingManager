from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from order.models import Order
from django.http import JsonResponse
from inventory.models import Material
from inventory.MaterialSerializer import MaterialSerializer
from .models import CarpenterEnquire
from .carpenter_enquire_serializer import CarpenterEnquireSerializer
from order.OrderSerializer import OrderSerializer

# Create your views here.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_carpenter_requests(request):
    try:
        user = request.user
        carpenter_enquiries = CarpenterEnquire.objects.filter(carpenter_id=user.id, organization_id=user.organization_id).all()
        if not carpenter_enquiries:
            return Response({'order_data': []}, status=status.HTTP_200_OK)
        orders = Order.objects.filter(carpenter_id = user.id, organization_id=user.organization_id).all()
        orders_data = []
        for order in orders:
            order_data = {
                'order_id': order.id,
                'product_name': order.product_name,
                'product_name_mal': order.product_name_mal,
                'product_description': order.product_description,
                'product_description_mal': order.product_description_mal,
                'status': order.enquiry_status
            }
            orders_data.append(order_data)
        return JsonResponse({'order_data': orders_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=404)
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def carpenter_request_accept(request, order_id):
    try:
        user = request.user
        carpenter_enquiries = CarpenterEnquire.objects.filter(order_id=order_id, carpenter_id=user.id, organization_id=user.organization_id).all()
        if not carpenter_enquiries:
            return Response({'message': "No carpenter enquiries found"}, status=status.HTTP_404_NOT_FOUND)
        # Update the status of each carpenter enquiry
        for enquiry in carpenter_enquiries:
            enquiry.status = 'checking'
            enquiry.save()  # Save the updated enquiry to the database
        # Also update the order's enquiry_status
        order = Order.objects.filter(id=order_id).first()
        if order:
            order.enquiry_status = 'checking'
            order.save()
        # Now you can serialize the updated carpenter enquiries and return the response
        # serializer = CarpenterEnquireSerializer(carpenter_enquiries, many=True)
        return Response({'message': "Success"}, status=status.HTTP_200_OK)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def carpenter_request_view(request, order_id):
    try:
        user = request.user
        order = Order.objects.filter(pk=order_id, organization_id=user.organization_id, carpenter_id=user.id).first()
        if order is None:
            return JsonResponse({'error': 'Order not found'}, status=404)
        order_serializer = OrderSerializer(order)
        material_ids = order_serializer.data['material_ids']
        material_data = []
        for material in material_ids:
            material_obj = Material.objects.filter(id= material, organization_id=user.organization_id).first()
            material_serializer = MaterialSerializer(material_obj)
            materials = material_serializer.data
            enquiry_obj = CarpenterEnquire.objects.filter(order_id= order_id, material_id=material, organization_id=user.organization_id).first()
            enquiry_serializer = CarpenterEnquireSerializer(enquiry_obj)
            materials['enquiry_data'] = enquiry_serializer.data
            materials.pop('price', None)
            materials.pop('quantity', None)
            materials.pop('category', None)
            materials.pop('stock_availability', None)
            material_data.append(materials)
        #Product Data
        product_data = {}
        if order.product:
            product_data = MaterialSerializer(order.product).data
        order_data = {
            'product': product_data,
            'order_id': order.id,
            'audios': order_serializer.data['audios'],
            'priority': order.priority,
            'images': order_serializer.data['images'],
            'product_name': order.product_name,
            'product_name_mal': order.product_name_mal,
            'product_description': order.product_description,
            'product_description_mal': order.product_description_mal,
            'product_length': order.product_length,
            'product_height':order.product_height,
            'product_width':order.product_width,
            'materials':material_data,
            'finish':order.finish,
            'event':order.event,
            'status': order.enquiry_status,
        }
        return JsonResponse({'data':order_data}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=404)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def carpenter_request_update(request):
    try:
        user = request.user
        data = request.data
        for request_item in data['data']:
            order_id = request_item['order_id']
            carpenter_enquiry = CarpenterEnquire.objects.filter(
                order_id=request_item['order_id'],
                material_id=request_item['material_id'],
                organization_id=user.organization_id,
                carpenter_id=user.id
            ).first()
            if not carpenter_enquiry:
                return JsonResponse({'error': 'Carpenter Enquiry not found'}, status=404)
            carpenter_enquiry.material_length = request_item['material_length']
            carpenter_enquiry.material_height = request_item['material_height']
            carpenter_enquiry.material_width = request_item['material_width']
            carpenter_enquiry.save()
        carpenter_enquiry_obj = CarpenterEnquire.objects.filter(order_id=order_id).all()
        serializer = CarpenterEnquireSerializer(carpenter_enquiry_obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def carpenter_request_respond(request, order_id):
    try:
        user = request.user
        carpenter_enquiries = CarpenterEnquire.objects.filter(order_id=order_id, organization_id=user.organization_id, carpenter_id=user.id).all()
        if not carpenter_enquiries:
            return JsonResponse({'error': 'Carpenter enquiries not found'}, status=404)
        for enquiry in carpenter_enquiries:
            if (
                enquiry.material_height is None or
                enquiry.material_length is None or
                enquiry.material_width is None
            ):
                e = 'Missing material details'
                return JsonResponse({'error': str(e)}, status=404)
            enquiry.status = 'completed'
            enquiry.save()
        order = Order.objects.filter(id = order_id).first()
        order.enquiry_status = 'completed'
        order.save()
        serializer = CarpenterEnquireSerializer(carpenter_enquiries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=404)