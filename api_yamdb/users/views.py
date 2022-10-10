from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api_yamdb import settings
from users.serializers import SignUpSerializer, GetTokenSerializer
from users.tokens import account_activation_token

User = get_user_model()


@api_view(['POST'])
def signup(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user, create = User.objects.get_or_create(
        username=serializer.validated_data['username'],
        email=serializer.validated_data['email'],
    )
    user.is_active = False
    user.confirmation_code = account_activation_token.make_token(user)
    user.save()
    send_mail(
        'Confirmation code has been sent to your adress',
        f'Ваш код подтверждения: {user.confirmation_code}',
        settings.EMAIL_HOST_USER,
        [request.data['email']]
    )
    return Response(serializer.validated_data)


@api_view(['POST'])
def get_token(request):
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    confirmation_code = serializer.validated_data.get('confirmation_code')
    user = get_object_or_404(User, username=username)
    if user.confirmation_code != confirmation_code:
        return Response(
            {'detail': 'Неверный код подверждения'
                       ' или пользователь не найден!'},
            status.HTTP_400_BAD_REQUEST
        )
    user.is_active = True
    user.save()
    token = AccessToken().for_user(user)

    return Response({'token': str(token)})
