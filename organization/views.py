from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Organization
from .serializers import OrganizationSerializer
from rest_framework.permissions import IsAuthenticated

# Create Organization
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_organization(request):
    user = request.user
     # Check the user is admin or not
    if user.isAdmin == False:
            return Response(
                {"message": f"You don't have permission to registered an organization: {user.organization_id.name}"},
                status=status.HTTP_400_BAD_REQUEST
            )
    # Check if the user has already registered an organization
    if user.organization_id:
        return Response(
            {"message": f"You have already registered an organization: {user.organization_id.name}"},
            status=status.HTTP_400_BAD_REQUEST
        )
    # Add 'created_by' explicitly to request data
    _data = request.data.copy()
    print("user.id ", user.id)
    _data["created_by"] = int(user.id)  # Ensure the user is assigned
    print(_data)
    # Proceed with organization creation
    serializer = OrganizationSerializer(data=_data)
    if serializer.is_valid():
        organization = serializer.save()
        # Assign the created organization to the current user's organization field
        user.organization_id = organization
        user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Retrieve All Organizations
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_organizations(request):
    organizations = Organization.objects.all()
    serializer = OrganizationSerializer(organizations, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# Retrieve Single Organization (Check if User Belongs to Organization)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_organization(request, organization_id):
    organization = get_object_or_404(Organization, id=organization_id)
    user = request.user
     # Check the user is admin or not
    if user.isAdmin == False:
            return Response(
                {"message":"You don't have permission to get organization details"},
                status=status.HTTP_400_BAD_REQUEST
            )
    if request.user.organization_id != organization:
        return Response({"error": "You do not have permission to access this organization."}, status=status.HTTP_403_FORBIDDEN)

    serializer = OrganizationSerializer(organization)
    return Response(serializer.data, status=status.HTTP_200_OK)

# Update Organization (Check Ownership)
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_organization(request, organization_id):
    organization = get_object_or_404(Organization, id=organization_id)
    user = request.user

    # Check if the user is an admin
    if not user.isAdmin:
        return Response(
            {"message": "You don't have permission to update organization details"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Ensure the user belongs to the organization they are trying to update
    if user.organization_id.id != organization.id:
        return Response(
            {"error": "You do not have permission to update this organization."},
            status=status.HTTP_403_FORBIDDEN
        )

    # Extract updated data
    updated_data = request.data.copy()

    # Fields to check for uniqueness across other organizations
    unique_fields = ["name", "email", "phone_number1", "phone_number2", "registration_number", "gst_number", "pan_number", "website"]

    for field in unique_fields:
        if field in updated_data:
            existing_org = Organization.objects.filter(**{field: updated_data[field]}).exclude(id=organization.id).first()
            if existing_org:
                return Response(
                    {field: f"This {field} is already used by another organization."},
                    status=status.HTTP_400_BAD_REQUEST
                )

    # Proceed with update
    serializer = OrganizationSerializer(organization, data=updated_data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delete Organization (Check Ownership)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_organization(request, organization_id):
    organization = get_object_or_404(Organization, id=organization_id)
    user = request.user
    # Check the user is admin or not
    if user.isAdmin == False:
            return Response(
                {"message":"You don't have permission to delete organization details"},
                status=status.HTTP_400_BAD_REQUEST
            )
    if request.user.organization_id != organization:
        return Response({"error": "You do not have permission to delete this organization."}, status=status.HTTP_403_FORBIDDEN)

    organization.delete()
    return Response({"message": "Organization deleted successfully"}, status=status.HTTP_204_NO_CONTENT)