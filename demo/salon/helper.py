import random
import re
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


def email_otp():
  r1 = random.randint(100000,999999)
  return r1


def Validate_Password(password):
    try:
    
        regex = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
        if (re.fullmatch(regex, password)):
            return True
        return False
    except:
        return Response({"msg": "Password is empty"})


def unique_email(email):
  """
  :return: All the users have the unique Email id.
  """
  res = User.objects.filter(email = email) # Get the Email from the User table. 
  return res


def get_tokens_for_user(user):
  """
  :return: refresh and access token generate when the user hit the login api.
  """
  refresh = RefreshToken.for_user(user) # Give the refresh token for the user
  return {
      'refresh': str(refresh),
      'access': str(refresh.access_token),
  }


def pagination(OFFSET,LIMIT,counter):
    if LIMIT > 100:
        LIMIT = 100 
    if counter == 0:
        OFFSET = OFFSET-LIMIT
        if OFFSET<=0:
            OFFSET = 0
    else:
        OFFSET = OFFSET+LIMIT
    return OFFSET,LIMIT
