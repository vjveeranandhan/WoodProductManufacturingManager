from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import InventoryCategory
from .InventoryCategorySerializer import InventoryCategorySerializer
from .MaterialSerializer import MaterialSerializer, CreateMaterialSerializer
from .models import Material, MaterialImages
from .tests import test_user_is_admin, test_user_has_organization, user_admin_and_org_check

#__________ Inventory Category api's ________________

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_categories(request):
    try:
        user = request.user
        check_result, check_message = user_admin_and_org_check(user, request, message="get categories")
        if not check_result:
            return Response({"message": check_message["message"]}, status=status.HTTP_403_FORBIDDEN)
        categories = InventoryCategory.objects.filter(organization_id=user.organization_id.id).all()
        serializer = InventoryCategorySerializer(categories, many=True)
        return Response(serializer.data)
    except:
        return Response({'message': "Somthing went wrong"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_category(request):
    try:
        user = request.user
        check_result, check_message = user_admin_and_org_check(user, request, message="create category")
        if not check_result:
            return Response({"message": check_message["message"]}, status=status.HTTP_403_FORBIDDEN)
        _data = request.data
        _data['organization_id'] = user.organization_id.id
        serializer = InventoryCategorySerializer(data=_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({'message': "Somthing went wrong"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_category(request, pk):
    try:
        user = request.user
        check_result, check_message = user_admin_and_org_check(user, request, message="get category")
        if not check_result:
            return Response({"message": check_message["message"]}, status=status.HTTP_403_FORBIDDEN)
        category = InventoryCategory.objects.filter(pk=pk, organization_id=user.organization_id.id).first()
        if category:
            serializer = InventoryCategorySerializer(category)
            return Response(serializer.data)
        return Response({"message": "Category not found!"},
                status=status.HTTP_403_FORBIDDEN)
    except InventoryCategory.DoesNotExist:
        return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_category(request, pk):
    try:
        user = request.user
        check_result, check_message = user_admin_and_org_check(user, request, message="update category")
        if not check_result:
            return Response({"message": check_message["message"]}, status=status.HTTP_403_FORBIDDEN)
        category = InventoryCategory.objects.filter(pk=pk, organization_id=user.organization_id.id).first()
        if category:
            serializer = InventoryCategorySerializer(category, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Category not found!"},
                status=status.HTTP_404_NOT_FOUND)
    except InventoryCategory.DoesNotExist:
        return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)    

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_category(request, pk):
    try:
        user = request.user
        check_result, check_message = user_admin_and_org_check(user, request, message="delete category")
        if not check_result:
            return Response({"message": check_message["message"]}, status=status.HTTP_403_FORBIDDEN)
        category = InventoryCategory.objects.filter(pk=pk, organization_id=user.organization_id.id).first()
        if category:
            category.delete()
            return Response({"message": "Category deleted successfully"}, status=status.HTTP_200_OK)
        return Response({"message": "Category not found!"},
                status=status.HTTP_404_NOT_FOUND)
    except InventoryCategory.DoesNotExist:
        return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

#__________ Inventory Material api's ________________

# GET all materials
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_materials(request):
    try:
        user = request.user
        check_result, check_message = user_admin_and_org_check(user, request, message="get materials")
        if not check_result:
            return Response({"message": check_message["message"]}, status=status.HTTP_403_FORBIDDEN)
        materials = Material.objects.filter(organization_id=user.organization_id.id).all()
        serializer = MaterialSerializer(materials, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except:
        return Response({'message': "Somthing went wrong"}, status=status.HTTP_400_BAD_REQUEST)

# POST to create a new material
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_material(request):
    try:
        user = request.user
        if user_admin_and_org_check(user, request, message= "create materials")[0] == False:
            return Response(
                {"message": user_admin_and_org_check(user, request)[1]['message']},
                status=status.HTTP_403_FORBIDDEN
            )
        _data = request.data.copy()
        category = InventoryCategory.objects.filter(pk=_data['category_id'], organization_id=user.organization_id.id).first()
        if not category:
            return Response({"message": "Category not found!"},
                status=status.HTTP_404_NOT_FOUND)
        material_images = request.FILES.getlist('material_image')
        _data.pop('image', None)
        _data['organization_id'] = user.organization_id.id
        serializer = CreateMaterialSerializer(data=_data)
        if serializer.is_valid():
            material_obj = serializer.save()
            for image in material_images:
                MaterialImages.objects.create(
                    image=image,
                    material_id=material_obj
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({'message': "Somthing went wrong"}, status=status.HTTP_400_BAD_REQUEST)

# GET a specific material by ID
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_material(request, pk):
    try:
        user = request.user
        check_result, check_message = user_admin_and_org_check(user, request, message="get materials")
        if not check_result:
            return Response({"message": check_message["message"]}, status=status.HTTP_403_FORBIDDEN)
        material = Material.objects.filter(pk=pk, organization_id=user.organization_id.id).first()
        serializer = MaterialSerializer(material)
        return Response(serializer.data)
    except Material.DoesNotExist:
        return Response({"error": "Material not found"}, status=status.HTTP_404_NOT_FOUND)

# PUT to update an existing material
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_material(request, pk):
    try:
        user = request.user
        check_result, check_message = user_admin_and_org_check(user, request, message="update materials")
        if not check_result:
            return Response({"message": check_message["message"]}, status=status.HTTP_403_FORBIDDEN)
        material = Material.objects.filter(pk=pk, organization_id=user.organization_id.id).first()
        if not material:
            return Response({"message": "Material not found!"},
                status=status.HTTP_404_NOT_FOUND)
        _data = request.data.copy()
        material_images = request.FILES.getlist('material_image')
        _data['id'] = material.id
        serializer = MaterialSerializer(material, data=_data, partial=True)
        if serializer.is_valid():
            material_obj = serializer.save()
            if material_images:
                MaterialImages.objects.filter(material_id=material_obj).all().delete()
                for image in material_images:
                    MaterialImages.objects.create(
                        image=image,
                        material_id=material_obj
                    )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Material.DoesNotExist:
        return Response({"error": "Material not found"}, status=status.HTTP_404_NOT_FOUND)

# DELETE a specific material by ID
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_material(request, pk):
    try:
        user = request.user
        check_result, check_message = user_admin_and_org_check(user, request, message="delete materials")
        if not check_result:
            return Response({"message": check_message["message"]}, status=status.HTTP_403_FORBIDDEN)
        material = Material.objects.filter(pk=pk, organization_id=user.organization_id.id).first()
        if not material:
            return Response({"message": "Material not found!"},
                status=status.HTTP_404_NOT_FOUND)
        material.delete()
        return Response({"message": "Material deleted successfully"}, status=status.HTTP_200_OK)
    except Material.DoesNotExist:
        return Response({"error": "Material not found"}, status=status.HTTP_404_NOT_FOUND)
