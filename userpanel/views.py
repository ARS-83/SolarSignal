from rest_framework.authtoken.models import Token
from rest_framework.decorators import  permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from django.contrib.auth import authenticate
from .models import CustomUser,Signal
from asgiref.sync import sync_to_async
from adrf.decorators import api_view
import json
import datetime
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

@api_view(['GET'])
async def get_signals(request: Request):
    if request.user.is_authenticated:    
        if CustomUser.objects.filter(username=request.user.username).exists():
            user = CustomUser.object.get(username=request.user.username)
            if user.is_block:
                return Response({'success': False, 'error': 'کاربر مسدود شده است'}, status=status.HTTP_403_FORBIDDEN)
            
            if user.subscription is None:
                return Response({'success': False, 'error': 'شما در یک اشتراک نیستید'}, status=status.HTTP_403_FORBIDDEN)
            if user.end_date_sub < datetime.datetime.now():
                return Response({'success': False, 'error': 'اشتراک شما به پایان رسیده است'}, status=status.HTTP_403_FORBIDDEN)
            signals = await sync_to_async(Signal.objects.all)()
            return Response({'success': True, 'signals': json.dumps(list(signals))}, status=status.HTTP_200_OK)

        else:
            return Response({'success': False, 'error': 'کاربر یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'success': False, 'error': 'کاربر وارد نشده است'}, status=status.HTTP_401_UNAUTHORIZED)    