from django.contrib.auth.models import User
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate,login
# class CustomTokenObtainPairView(TokenObtainPairView):
#     permission_classes = (AllowAny,)

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class LoginView(APIView):

    def post(self, request):
        try:
            data = {
                "access_token":"",
                "refresh_token":"",
                "user_info":{
                    "user_id":1,
                    "user_name":""
                }
            }
            user_name = request.data.get("username")
            password = request.data.get("password")

            user_obj = authenticate(username=user_name, password=password)

            if user_obj is not None:
                token = get_tokens_for_user(user_obj)
                data["access_token"] = token.get("access")
                data["refresh_token"] = token.get("refresh")
                data["user_info"]["user_id"] = user_obj.id
                data["user_info"]["user_name"] = user_obj.username

                return Response({"status":200, "data":data})
            else:
                return Response({'msg': 'Invaild username or password'}, status=404)
        except Exception as e:
            return Response({"message": str(e)}, status=500) 
        

class RegisterView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        """
        this method for user create
        """
        username = request.data.get('username')
        password = request.data.get('password')
        password_2 = request.data.get('password_2')

        try:
            
            # check the if username and passwird is null
            if not username or not password:
                return Response({"error": "Missing credentials"}, status=status.HTTP_400_BAD_REQUEST)

            if not password == password_2:
                return Response({"error":"Invaild"}, status=status.HTTP_400_BAD_REQUEST)
            


            if User.objects.filter(username=username).exists():
                return Response({"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.create_user(username=username, password=password)
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": str(e)}, status=500)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
