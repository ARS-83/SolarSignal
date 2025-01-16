from rest_framework.authtoken.models import Token
from rest_framework.decorators import  permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from django.contrib.auth import authenticate
from .models import CustomUser
from asgiref.sync import sync_to_async
from adrf.decorators import api_view

@api_view(['POST'])
@permission_classes([AllowAny])
async def register(request: Request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')
    name = request.data.get('name')
    phone_number = request.data.get('phone_number')
    
    # Use async ORM functions
    user = await sync_to_async(CustomUser.objects.create_user)(
        username=username,
        password=password,
        email=email,
        name=name,
        phone_number=phone_number,
        is_active=True,
    )
    token = await sync_to_async(Token.objects.create)(user=user)
    return Response({'success': True, 'token': token.key}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
async def login(request: Request):
    unknown = 'Unknown'
    username = request.data.get('username', "Unknown")
    password = request.data.get('password', "Unknown")
    if username == unknown and password == unknown:
        return Response({'success': False, 'error': 'مقادیر ارسالی دچار مشکل میباشند'})

    user = await sync_to_async(authenticate)(username=username, password=password)

    if user is not None:
        token, created = await sync_to_async(Token.objects.get_or_create)(user=user)
        return Response({'success': True, 'token': token.key}, status=status.HTTP_200_OK)
    else:
        return Response({'success': False, 'error': 'کاربری با این مشخصات یافت نشد'},
                        status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])
async def check_login(request: Request):

    if request.user.is_authenticated:
        return Response({'success': True, 'message': 'user is logged in'}, status=status.HTTP_200_OK)
    else:
        return Response({'success': False, 'message': 'user is not logged in'}, status=status.HTTP_200_OK)