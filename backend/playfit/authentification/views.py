from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.conf import settings
from django.views import View
from django.shortcuts import render
from django.contrib.auth.password_validation import validate_password
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from social_django.utils import load_strategy
from social_core.backends.google import GoogleOAuth2
from social_core.exceptions import AuthForbidden
from utilities.encrypted_fields import hash
from utilities.expiring_password_reset_token import ExpiringPasswordResetTokenGenerator
from .models import CustomUser
from .serializers import CustomUserSerializer, CustomUserRetrieveSerializer, CustomUserUpdateSerializer, CustomUserDeleteSerializer
from .utils import generate_username_with_number, get_user_birthdate, generate_uid_from_id, get_id_from_uid

class RegisterView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=CustomUserSerializer,
        responses={
            201: openapi.Response("User registered successfully", CustomUserSerializer),
            400: "Invalid data",
        },
        operation_description="Register a new user with username, email, height, weight, date of birth, and password."
    )
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="User login with username or email and password.",
        responses={
            200: openapi.Response("User logged in successfully"),
            400: "Invalid credentials",
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['username', 'password']
        )
    )
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user is None:
            try:
                if not email:
                    raise CustomUser.DoesNotExist
                user = CustomUser.objects.get(email_hash=hash(email))
                user = authenticate(username=user.username, password=password)
            except CustomUser.DoesNotExist:
                return Response({'error': "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="User logout.",
        responses={
            200: openapi.Response("User logged out successfully"),
            400: "Invalid credentials",
        }
    )
    def post(self, request):
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
            return Response({'success': "Successfully logged out"}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({'error': "Token not found or already logged out"}, status=status.HTTP_400_BAD_REQUEST)

class GoogleOAuthLoginView(APIView):
    permission_classes = [AllowAny]

    def get_user_data(self, request, token):
        strategy = load_strategy(request)
        backend = GoogleOAuth2(strategy)
        backend.do_auth(token)
        user_data = backend.user_data(token)

        return user_data

    def create_user(self, user_data, birth_date):
        email = user_data.get('email')
        user = CustomUser.objects.create_user(
            email=email,
            email_hash=hash(email),
            username=generate_username_with_number(user_data.get('name') or email.split('@')[0]),
            password=None,
            registration_method='google',
            date_of_birth=birth_date,
            height=250,
            weight=250,
        )
        user.is_active = True
        user.save()

        return user

    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({'status': 'error', 'message': 'No token provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_data = self.get_user_data(request, token)
            email = user_data.get('email')

            if not email:
                return Response({'status': 'error', 'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = CustomUser.objects.get(email_hash=hash(email))
                if user.registration_method in ['google', 'email']:
                    login(request, user)
                    django_token, _ = Token.objects.get_or_create(user=user)
                    return Response({'status': 'success', 'message': 'Logged in using Google', 'token': django_token.key}, status=status.HTTP_200_OK)
                else:
                    return Response({'status': 'error', 'message': 'Cannot log in with email and password'}, status=status.HTTP_400_BAD_REQUEST)
            except CustomUser.DoesNotExist:
                birth_date = get_user_birthdate(token)
                if not birth_date:
                    return Response({'status': 'error', 'message': 'Aucune date de naissance renseignée, impossible de vérifier votre âge'}, status=status.HTTP_400_BAD_REQUEST)

                user = self.create_user(user_data, birth_date)
                login(request, user)
                django_token, _ = Token.objects.get_or_create(user=user)
                return Response({'status': 'success', 'message': 'Account created and logged in', 'token': django_token.key}, status=status.HTTP_200_OK)
        except AuthForbidden:
            return Response({'status': 'error', 'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

class UserView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get user data.",
        responses={
            200: openapi.Response("User data", CustomUserRetrieveSerializer),
        }
    )
    def get(self, request):
        serializer = CustomUserRetrieveSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=CustomUserUpdateSerializer,
        operation_description="Update user data.",
        responses={
            200: openapi.Response("User data updated", CustomUserUpdateSerializer),
            400: "Invalid data",
        }
    )
    def patch(self, request):
        serializer = CustomUserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=CustomUserDeleteSerializer,
        operation_description="Delete (anonymize) the current user's data.",
        responses={
            200: openapi.Response("User data deleted"),
            400: "Invalid data",
        }
    )
    def delete(self, request):
        serializer = CustomUserDeleteSerializer(request.user, data=request.data)
        if serializer.is_valid():
            request.user.anonynimze_user()
            return Response({'message': 'Your data has been anonymized successfully.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=400)

class ResetPasswordRequestView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Send a password reset email to the current user.",
        responses={
            200: openapi.Response("Password reset email sent"),
        }
    )
    def get(self, request):
        user = request.user
        token_generator = ExpiringPasswordResetTokenGenerator()
        token = token_generator.make_signed_token(user)
        uid = generate_uid_from_id(user.id)
        reset_link = f"{settings.SERVER_BASE_URL}/api/auth/reset_password?uid={uid}&token={token}"

        send_mail(
            subject="Réinitialisation du mot de passe",
            message="Si vous voyez ce message, c'est que votre client email ne supporte pas les messages HTML.",
            html_message=render_to_string('authentification/reset_password_email.html', {'user': user, 'reset_link': reset_link}),
            from_email="no-reply@playfit.com",
            recipient_list=[user.email],

        )
        return Response({'message': 'Password reset email sent'}, status=status.HTTP_200_OK)

class ResetPasswordView(View):
    def get(self, request):
        uid = request.GET.get('uid')
        token = request.GET.get('token')

        if not uid or not token:
            return render(request, "authentification/reset_password.html", {'message': 'Lien non valide'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_id = get_id_from_uid(uid)
            user = CustomUser.objects.get(id=user_id)
        except (UnicodeDecodeError, CustomUser.DoesNotExist):
            return render(request, "authentification/reset_password.html", {'message': 'Lien non valide'}, status=status.HTTP_400_BAD_REQUEST)

        token_generator = ExpiringPasswordResetTokenGenerator()
        if not token_generator.check_signed_token(user, token):
            return render(request, "authentification/reset_password.html", {'message': 'Le lien a expiré'}, status=status.HTTP_400_BAD_REQUEST)

        return render(request, "authentification/reset_password.html", {'uid': uid, 'token': token}, status=status.HTTP_200_OK)

    def post(self, request):
        uid = request.POST.get('uid')
        token = request.POST.get('token')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not uid or not token or not password:
            return render(request, "authentification/reset_password.html", {'message': 'Données manquantes'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_id = get_id_from_uid(uid)
            user = CustomUser.objects.get(id=user_id)
        except (UnicodeDecodeError, CustomUser.DoesNotExist):
            return render(request, "authentification/reset_password.html", {'message': 'Données manquantes'}, status=status.HTTP_400_BAD_REQUEST)

        token_generator = ExpiringPasswordResetTokenGenerator()
        if not token_generator.check_signed_token(user, token):
            return render(request, "authentification/reset_password.html", {'message': 'Le lien a expiré'}, status=status.HTTP_400_BAD_REQUEST)

        if password != confirm_password:
            return render(request, "authentification/reset_password.html", {'error': 'Les mots de passe ne correspondent pas'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(password, user)
        except ValidationError as e:
            return render(request, "authentification/reset_password.html", {'error': e.messages[0]}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(password)
        user.save()

        return render(request, "authentification/reset_password.html", {'message': 'Mot de passe réinitialisé'}, status=status.HTTP_200_OK)
