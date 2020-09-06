from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()



class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('phone','password')
        extra_kwargs = {'password': {'write_only': True},}

        def create(self, validated_data):
            user = User.objects.create(**validated_data)
            return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        Model = User
        fields = {'id', 'phone', 'first_login'}




class LoginSerializer(serializers.ModelSerializer):
    phone = serializers.CharField()
    password= serializers.CharField(style={'input_type': 'password'}, trim_whitespace= False)

    def validate(self,data):
        print(data)
        phone= data.get('phone')
        password= data.get('password')

        if phone and password:
            if User.objects.filter(phone=phone).exists():
                print(phone,password)
                user = authenticate(request=self.context.get('request'),phone=phone,password=password  )
                print(user)
            else:
                msg = {
                    'status': False,
                    'detail': 'phone number not found',

                }
                raise serializers.ValidationError(msg)

            if not user:
                msg = {
                    'status': False,
                    'detail': 'phone amd password not match'

                }
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg ={
                'status': False,
                'detail': 'phone and password not found'

            }
            raise serializers.ValidationError(msg,code='authorization')

        data['user']= user
        return data

