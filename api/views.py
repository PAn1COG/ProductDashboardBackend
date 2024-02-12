from base64 import urlsafe_b64decode, urlsafe_b64encode
from rest_framework import status
from .models import Item, Category
from .serializers import CategorySerializer, ItemSerializer, UserSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.encoding import force_bytes

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getAllItems(request):
    queryset = Item.objects.all()
    search_param = request.GET.get('search')
    order_by_param = request.GET.get('order_by')
    search_sku = request.GET.get('sku')
    search_name = request.GET.get('name')
    search_category = request.GET.get('category')
    search_stock_status = request.GET.get('stock_status')
    if search_param:
        queryset = queryset.filter(name__icontains=search_param)
    
    if order_by_param:
        queryset = queryset.order_by(order_by_param)
    
    if search_sku:
        queryset = queryset.filter(SKU__icontains=search_sku)

    if search_name:
        queryset = queryset.filter(name__icontains=search_name)

    if search_category:
        category = Category.objects.get(name=search_category)
        queryset = queryset.filter(category=category)
    
    if search_stock_status:  
        queryset = queryset.filter(stock_status=search_stock_status)

    if not queryset.exists():
        return Response(0,status=status.HTTP_404_NOT_FOUND)
    serializer = ItemSerializer(queryset, many = True)
    return Response(serializer.data)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getAllCategories(request):
    # 
    # add sorting and pagination
    # (pageNo - 1)pageSize
    # 
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many = True)
    return Response(serializer.data)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getItem(request):
    SKU = request.GET.get('SKU')
    if not SKU :
        return Response("Please provide SKU",status=status.HTTP_400_BAD_REQUEST)
    item = Item.objects.get(SKU=SKU)
    serializer = ItemSerializer(item, many = False)
    return Response(serializer.data)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def createCategory(request):
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def createItem(request):
    serializer = ItemSerializer(data=request.data)
    if(serializer.is_valid()):
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)
    return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def updateItem(request):
    item = Item.objects.get(SKU=request.GET.get('SKU'))
    serializer = ItemSerializer(instance=item, data= request.data)
    
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def deleteItem(request):
    SKU = request.GET.get('SKU')
    if not SKU :
        return Response('Please provide SKU')
    item = Item.objects.filter(SKU=SKU)
    item.delete()
    return Response('deleted')

@api_view(['DELETE'])
def delete_category(request):
    try:
        key = request.GET.get('category')
        if not key : 
            return Response('provide category to delete.')
        category = Category.objects.get(pk=key)
    except Category.DoesNotExist:
        return Response({"message": "Category does not exist"}, status=status.HTTP_404_NOT_FOUND)

    # If category exists, delete it and its associated items
    category.delete()
    return Response({"message": "Category and associated items deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def login(request):
    user = get_object_or_404(User, username=request.data['username'])
    if not user.check_password(request.data['password']):
        return Response("missing user", status=status.HTTP_403_FORBIDDEN)
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(user)
    return Response({'token': token.key, 'user': serializer.data})
   
@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = User.objects.get(username=request.data['username'])
        user.set_password(request.data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return Response({'token': token.key, 'user': serializer.data})
    return Response(serializer.errors, status=status.HTTP_200_OK)
    

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def testToken(request):
    return Response("passed!")

@api_view(['POST'])
def forgot_password(request):
    email = request.data.get('email')
    if email:
        user = User.objects.filter(email=email).first()
        if user:
            token = default_token_generator.make_token(user)
            # Build password reset link
            uid = urlsafe_b64encode(force_bytes(user.pk))
            reset_link = f"http://3.19.242.75:8000/authentication/reset-password/{uid}/{token}"
            # Send reset link via email
            subject = "Password Reset"
            message = render_to_string('reset_password_email.html', {
                'reset_link': reset_link,
            })
            send_mail(subject, message, 'from@example.com', [email])
        return Response("Password reset link sent if the email exists.", status=status.HTTP_200_OK)
    return Response("Email field is required.", status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def reset_password(request, uidb64, token):
    # Decode user ID from base64
    try:
        uid = urlsafe_b64decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        # Update user's password
        new_password = request.data.get('new_password')
        if new_password:
            user.set_password(new_password)
            user.save()
            return Response("Password reset successfully.", status=status.HTTP_200_OK)
        return Response("New password is required.", status=status.HTTP_400_BAD_REQUEST)
    return Response("Invalid reset link or token.", status=status.HTTP_400_BAD_REQUEST)