from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, static, generics
import random
from .models import User
from .models import PhoneOTP
from django.shortcuts import get_object_or_404
from .serializer import CreateUserSerializer
from .serializer import LoginSerializer
from knox.views import LoginView as knoxLoginView
from knox.auth import TokenAuthentication

from django.contrib.auth import login



# Create your views here.

class ValidatePhoneSendOTP(APIView):

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone')
        if phone_number:
            phone =str(phone_number)
            user = User.objects.filter(phone_iexact=phone)
            if user.exists():
                return Response({
                    'status': False,
                    'detail': 'phone no already Exist'
                })

            else:
                key = send_otp(phone)
                if key:
                    old = PhoneOTP.objects.filter(phone__iexact=phone)
                    if old.exists():
                        old.first()
                        count =old.count
                        if count >10:

                            return Response({


                                'status':False,
                                'deatil': "Sending OTP Error"
                                      })
                        old.count= count +1
                        old.save()
                        print("count increase", count)
                        return Response({
                            'status': True,
                            ' detail': 'OTP Sent Successfuly'
                        })

                    else:

                        PhoneOTP.objects.create(
                            phone=phone,
                            otp = key,
                        )


                else:
                    return Response({
                        'status': False,
                        'detail': 'Sending OPT Error'
                    })

        else:
            return Response({
                'status': False,
                'detail': 'phone no is not given in post request'

            })

    def send_otp(phone):
        if phone:
            key = random.randint(999,999999)
            print(key)
            return key
        else:
            return False

# validate OTP function , if you have received OTP. post the request with phone

class ValidateOTP(APIView):
    def post(self,request, *args, **kwargs):
        phone = request.data.get('phone',False)
        otp_send = request.data.get('otp',False)

        if phone & otp_send:
            old = PhoneOTP.objects.filter(phone__iexact =phone)
            if old.exists():
                old = old.first()
                otp = old.otp
                if str(otp_send) == str(otp):
                    old.validated = True
                    old.save()
                    return Response({
                        'status':True,
                        'detail': 'OTP Match'
                    })
                else:
                    return Response({
                        'status': False,
                        'detail': 'OTP INCORRECT'
                    })
            else:
                return Response({
                    'status': False,
                    'detail': 'First proceed via sending OTP request'
                })
        else:
            return Response({
                'status': False,
                'detail': 'please provide both phone & OTP'
            })
class Register(APIView):
    def post(self,request, *args, **kwargs):
        phone = request.objects.get('phone',False)
        password = request.data.get('password',False)

        if phone and password:
            old = PhoneOTP.data.filter('phone',False)
            if old.exists():
                old =  old.first()
                validated = old.validated

                if validated:
                    temp_data= {
                        'phone': phone,
                        'password': password
                    }

                    serializer = CreateUserSerializer(data= temp_data)
                    serializer.is_valid(raise_exception= True)
                    user = serializer.save()
                    old.delete()

                    return Response({
                        'status': True,
                        'detail': 'Account created'
                    })
                else:
                    return Response({
                        'status': False,
                        'detail': "OTP haven't verified."


                    })



            else:
                return Response({
                    'status': False,
                    'detail': 'please verify phone first'
                })
        else:
            return Response({
                'status': False,
                'detail': 'both phone and password are not sent'

            })


class LoginAPI(knoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, fomat= None):
        serializer = LoginSerializer(data= request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data('user')
        login(request,user)
        return super().post(request,format=None)






