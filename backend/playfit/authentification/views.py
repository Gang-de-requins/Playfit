from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login
from .serializers import CustomUserSerializer, ProductSerializer
from .models import CustomUser, Product
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from social_django.utils import load_strategy
from social_core.backends.google import GoogleOAuth2
from social_core.exceptions import AuthForbidden
from .utils import generate_username_with_number, get_user_birthdate


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
                user = CustomUser.objects.get(email=email)
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
                user = CustomUser.objects.get(email=email)
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


# Create your views here

class DocsView(APIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def list(self, request, *args, **kwargs):
        data = list(Product.objects.all().values())
        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        data = list(Product.objects.filter(id=kwargs['pk']).values())
        return Response(data)

    def create(self, request, *args, **kwargs):
        product_serializer_data = ProductSerializer(data=request.data)
        if product_serializer_data.is_valid():
            product_serializer_data.save()
            status_code = status.HTTP_201_CREATED
            return Response({"message": "Product Added Sucessfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "please fill the datails", "status": status_code})

    def destroy(self, request, *args, **kwargs):
        product_data = Product.objects.filter(id=kwargs['pk'])
        if product_data:
            product_data.delete()
            status_code = status.HTTP_201_CREATED
            return Response({"message": "Product delete Sucessfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Product data not found", "status": status_code})

    def update(self, request, *args, **kwargs):
        product_details = Product.objects.get(id=kwargs['pk'])
        product_serializer_data = ProductSerializer(
            product_details, data=request.data, partial=True)
        if product_serializer_data.is_valid():
            product_serializer_data.save()
            status_code = status.HTTP_201_CREATED
            return Response({"message": "Product Update Sucessfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Product data Not found", "status": status_code})