import environ
import datetime
from rest_framework.response import Response
from salon.serializer import *
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from django.utils import timezone
from salon.helper import *
from rest_framework.generics import GenericAPIView,ListAPIView
from salon.renderers import UserRenderer
from django.contrib.auth.hashers import check_password,make_password
from rest_framework.permissions import IsAuthenticated
from salon.models import *
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter,OrderingFilter
import stripe
from django.conf import settings
from django.http import HttpResponse


env = environ.Env()
environ.Env.read_env()
EMAIL_FROM = env('EMAIL_FROM')


OFFSET = 0 # Give the OFFSET for the pagination
LIMIT = 2 # Limit of the pagination.


# Create your views here.
class UserRegistrationView(GenericAPIView):
  """
  :return: Register user and send the email for user verification.
  """
  serializer_class = UserRegistrationSerializer
  renderer_classes = [UserRenderer]
  def post(self, request, format=None):
    fields = ('username', 'first_name', 'last_name', 'email', 'password','password1') # Check all the fields in the serializer or not.
    for field  in request.data.keys():
      if field not in fields:
        return Response({'msg': 'Fields Incorrect'})
    confirm_password = request.data.get('password1') #Request the Email from the user)
    # confirm_password = request.data.get('password1') #Request the Email from the user
    email = request.data.get('email') #Request the Email from the user
    username = request.data.get('username') # Request the username from the user
    password = request.data.get('password') # Request the password from the user
    first_name = request.data.get('first_name') # Request th0e first name from the user
    last_name = request.data.get('last_name') # Request the last name from the user
    if not email or not username or not password or not first_name or not last_name: # check the parameters for the email,username,password,firstname,lastname.
       return Response({'msg': 'Invalid parameters'})
    pass_bool = Validate_Password(password) # Validate the password.
    if not pass_bool:
      return Response({'msg': 'Enter valid passoword'})
    res = unique_email(email) # Email is unique for every user.
    if res:
      return Response({'msg': 'Email or username already Exists'})
    if password!=confirm_password:
      return Response({'msg': 'Password doesnot match'})
    serializer = UserRegistrationSerializer(data=request.data) # serializer the data
    serializer.is_valid(raise_exception=True) # if fields is valid
    user = User.objects.create(username=username,password=password,email=email,first_name=first_name,last_name=last_name)
    user.password= make_password(password)
    user.save()
    otp = email_otp() # six digits otp send to your email.
    user_obj = User.objects.get(username=username) # Get the username from the user table.
    profile = Profile(user=user_obj,auth_token=otp)
    profile.save()
    # sending otp in user email while register
    EMAIL_FROM = env('EMAIL_FROM')
    EMAIL_FROM = env('EMAIL_FROM')
    subject = 'Verify Email Otp '
    message = f'Hi {username}, OTP for Email Verification is {otp}.'
    email_from = EMAIL_FROM
    recipient_list = [email]
    send_mail( subject, message, email_from, recipient_list)
    return Response({'msg':'Registration Successfull, A OTP Verification code has been send to your Email'}, status = 201)


class VerifyEmailSecondTime(GenericAPIView):
  serializer_class = VerifyOtpSerializer
  renderer_classes = [UserRenderer]
  def post(self,request):
    """
    :return: send OTP second time for email verification when user is to forgot to Enter the OTP for first time.
    """
    email = request.data.get('email') # Enter the same mail you enter registration time
    if not email: # check the parameter of the email
      return Response({'msg': 'Invalid parameters'})
    res = User.objects.filter(email=email).values('id') # Get the Email from the user table
    if res:
      otp = email_otp() # six digits otp send to your email.
      EMAIL_FROM = env('EMAIL_FROM')
      EMAIL_FROM = env('EMAIL_FROM')
      subject = 'Verify Email Otp '
      message = f'Hi {email}, OTP for Email Verification is {otp}.'
      email_from = EMAIL_FROM
      recipient_list = [email]
      send_mail( subject, message, email_from, recipient_list) # send otp thrugh email if the email is stored in the database
      profile  = Profile.objects.get(user=res[0]['id'])
      profile.auth_token=otp
      profile.created_at=datetime.datetime.now(timezone.utc)
      profile.save()
      return Response({'msg':' A Verification code has been send to your Email'}, status = 201)
    return Response({'msg':"Email Doesn't exists"}, status = 204)


class VerifyOtpForEmailVerification(GenericAPIView):
  serializer_class = VerifyOtpSerializer
  renderer_classes = [UserRenderer]
  def post(self,request):
    """
    :return: Send OTP through Email When the user hit the register api. 
    """
    user_id = request.data.get('user_id')
    auth_token = request.data.get('auth_token')
    if not user_id or not auth_token:
      return Response({'msg': 'Invalid parameters'})
    res = Profile.objects.filter(user_id=user_id).values()
    if res:  #checks if there is any user with this id
      otp_time=res[0]['created_at']
      time_change = datetime.timedelta(days=1)
      new_time=otp_time+time_change
      now = datetime.datetime.now(timezone.utc)
      if new_time>= now:
          if str(res[0]['user_id'])==user_id and res[0]['auth_token']==auth_token:
            res.update(is_verified=True)
            return Response({"status": "Otp Verified"}, status = 200)
          return Response({"status": "Otp Incorrect"}, status = 400)
      return Response({"status": "Verification OTP Expired"}, status = 400)
    return Response({"status": "No user found"}, status = 400)





# user login view
class UserLoginView(GenericAPIView):
  serializer_class = UserLoginSerializer
  renderer_classes = [UserRenderer]
  def post(self, request, format=None,):
    """
    :return: username and password for login and correct params.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
      return Response({'msg': 'Invalid parameters'})
    user = User.objects.filter(username=username).values('id','is_superuser')
    if user:
      if not user[0]['is_superuser']:
        try:
          res=Profile.objects.get(user=user[0]['id'])
        except:
          return Response({'msg':'Please continue with google to login'})
        if res:
          if res.is_verified == False:
            return Response({'msg': 'email not verified'})

      serializer = UserLoginSerializer(data=request.data)
      serializer.is_valid(raise_exception=True)
      user = authenticate(username=username, password=password)
      if user is not None:
        # generate token when user login for authenticating
          token = get_tokens_for_user(user) 
          # login(request,user)
          return Response({'token': token, 'msg': 'Login Success'})
      else:
          return Response({'errors': {'non_field_errors': ['Username or Password is not Valid']}}, status = 404)
    return Response({'msg': 'No user found'}, status = 404)


class SendPasswordEmailView(GenericAPIView):
  serializer_class = SendPasswordResetEmailSerializer
  renderer_classes = [UserRenderer]
  def post(self, request, formate=None):
    """
    :return: Reset password email successfully send.
    """
    serializers = SendPasswordResetEmailSerializer(data=request.data)
    serializers.is_valid(raise_exception=True)
    return Response({'msg':'Email Sent Successful'}, status = 200)


# user reset password view
class UserPasswordResetView(GenericAPIView):
  serializer_class = UserPasswordResetSerializer
  renderer_classes = [UserRenderer]
  def post(self, request, uid, token, format=None):
    """
    :return: Password reset through Email when the user forgot the pasword.
    """
    serializers = UserPasswordResetSerializer(data=request.data, context={'uid':uid, 'token':token, 'user':request.user})
    serializers.is_valid(raise_exception=True)
    return Response({'msg':'Password Reset Successful'}, status = 200)


class UserChangePasswordView(GenericAPIView):
  serializer_class = UserChangePasswordSerializer
  renderer_classes = [UserRenderer]
  permission_classes = [IsAuthenticated]
  def post(self, request, format=None):
    """
    :return: password change when the user is logged in.
    """
    fields = ('old_password','password')
    for field  in request.data.keys():
      if field not in fields:
        return Response({'msg': 'Fields Incorrect'})
    old_password =request.data.get('old_password')
    password =request.data.get('password')
    id = self.request.user.id
    pass_get = User.objects.filter(id=id).values('password')
    if check_password(old_password,pass_get[0]['password']): 
      # serializer = UserChangePasswordSerializer(data=request.data, context={'user':request.user})
      # serializer.is_valid(raise_exception=True)
      user_object=User.objects.get(id=id)
      user_object.password= make_password(password)
      user_object.save() 
      return Response({'msg':'Password Changed Successfully'}, status = 200)
    return Response({'msg':'Old Password entered incorrectly '}, status=403)


class UpdateUserProfile(GenericAPIView):
  serializer_class = UserUpdateProfileSerializer
  renderer_classes = [UserRenderer]
  def put(self, request, id):
    try:
      user = User.objects.get(id=id)
      serializer = UserUpdateProfileSerializer(user, data=request.data)
      serializer.is_valid()
      serializer.save()
      return Response({"status":"success", "data": serializer.data}, status = 200)
    except:
      return Response({"status":"User Not Found"}, status = 400)


class DeleteUserProfile(GenericAPIView):
  renderer_classes = [UserRenderer]
  def delete(self, request,id):
    try:
      user = User.objects.get(id=id) 
      user.delete()
      return Response({"Msg":"User Deleted Successfully"},status=200)
    except:
      return Response({"status":"User Not Found"}, status = 400)


class GetAllProduct(GenericAPIView):
  serializer_class = ProductSerializer
  renderer_classes = [UserRenderer]
  def get(self, request):
    """
    :return: All products stored in database
    check the permission to view the products
    """
    items = Product.objects.all()
    serializer = ProductSerializer(items, many=True)
    return Response({"status": "success", "data": serializer.data}, status = 200)


class GetProductById(GenericAPIView):
  serializer_class = ProductSerializer
  renderer_classes = [UserRenderer]
  def get(self, request, id=None):
    """
    :return: Get all Product by id.
    """
    try:
      if id:
        item = Product.objects.get(id=id)
        serializer = GetProductSerializer(item)
        return Response({"status": "success", "data": serializer.data}, status = 200)
    except:
      return Response({"status": "Not available"}, status = 400)


class ProductPaginatioNext(GenericAPIView):
  """
  :return: move to next page if the user hit's the api.
  """
  serializer_class = ProductSerializer
  renderer_classes = [UserRenderer]
  def get(self,request,LIMIT=2):
    global OFFSET
    OFFSET,LIMIT = pagination(OFFSET,LIMIT,1)
    res = Product.objects.all()
    if OFFSET>=len(res):
      OFFSET = OFFSET-LIMIT
    res = Product.objects.all()[OFFSET:OFFSET+LIMIT]
    serializer =  ProductSerializer(res, many=True)
    return Response({"status": "success", "data": serializer.data}, status = 200)


class ProductPaginationPrevious(GenericAPIView):
  """
  :return: Move to the previous page if the user hit the api.
  """
  serializer_class = ProductSerializer
  renderer_classes = [UserRenderer]
  def get(self,request,LIMIT=2):
    global OFFSET
    OFFSET,LIMIT = pagination(OFFSET,LIMIT,0)
    res = Product.objects.all()[OFFSET:OFFSET+LIMIT]
    serializer =  ProductSerializer(res, many=True)
    return Response({"status": "success", "data": serializer.data}, status=200)


class GetProductByCategory(GenericAPIView):
  """
  :return: All the product shown by the category.
  """
  serializer_class = ProductSerializer
  renderer_classes = [UserRenderer]
  def get(self,request,id):
    res = Product.objects.filter(category=id)
    serializer =  ProductSerializer(res, many=True)
    return Response({"status": "success", "data": serializer.data}, status = 200)


class GetAllCategory(GenericAPIView):
  """
  :return: Get all the category from the category table.
  """
  serializer_class = CategorySerializer
  renderer_classes = [UserRenderer]
  def get(self, request):
      items = Category.objects.all()
      serializer = CategorySerializer(items, many=True)
      return Response({"status": "success", "data": serializer.data}, status = 200)


class CategoryPaginatioNext(GenericAPIView):
  """
  :return: Move to the next page if the user hit the API.
  """
  serializer_class = CategorySerializer
  renderer_classes = [UserRenderer]
  def get(self,request,LIMIT=2):
    global OFFSET
    OFFSET,LIMIT = pagination(OFFSET,LIMIT,1)
    res = Category.objects.all()
    if OFFSET>=len(res):
      OFFSET = OFFSET-LIMIT
    res = Category.objects.all()[OFFSET:OFFSET+LIMIT]
    serializer =  CategorySerializer(res, many=True)
    return Response({"status": "success", "data": serializer.data}, status = 200)


class CategoryPaginationPrevious(GenericAPIView):
  serializer_class = CategorySerializer
  renderer_classes = [UserRenderer]
  def get(self,request,LIMIT=2):
    """
    :return: Move to the previous page if the user hit the url.
    category pagination 
    """
    global OFFSET
    OFFSET,LIMIT = pagination(OFFSET,LIMIT,0)
    res = Category.objects.all()[OFFSET:OFFSET+LIMIT]
    serializer =  CategorySerializer(res, many=True)
    return Response({"status": "success", "data": serializer.data}, status = 200)


class FilterProduct(ListAPIView):
  queryset = Product.objects.all()
  serializer_class = ProductSerializer
  filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
  filterset_fields = ['id','name','price']
  search_fields = ['id','^name']
  ordering_fields = ['id','name','price']


class test(GenericAPIView):
  def GET(self,request):
    return Response({"status": "success"}, status = 200)
  def POST(self,request):
    return Response({"status": "success"}, status = 200)


class AddProductCart(GenericAPIView):
  serializer_class = AddCartSerializer
  renderer_classes = [UserRenderer]
  # permission_classes = [IsAuthenticated]
  def post(self,request,id): 
    try:
      user = User.objects.get(id=id)
      product = Product.objects.get(id=request.data['product_id'])
      quantity = int(request.data['quantity'])   
      try:
        cart=Cartitems.objects.get(user=user,product=product)
        cart.quantity += quantity
      except:
        cart=Cartitems.objects.create(user=user,product=product,quantity=quantity,created_at=datetime.datetime.now)
      cart.save()
      serializer = AddCartSerializer(cart)
      return Response({"status":"success", "data": serializer.data}, status = 200)
    except:
      return Response({"status":"Not Found"}, status = 400)


class ViewCartProduct(GenericAPIView):
  serializer_class = ViewCartSerializer
  renderer_classes = [UserRenderer]
  def get(self, request,id):
    user = User.objects.get(id=id)
    cart = Cartitems.objects.filter(user=user)
    serializer = ViewCartSerializer(cart,many=True)
    return Response({"status": "success", "data": serializer.data}, status = 200)


class DeleteCartItemById(GenericAPIView):
  serializer_class = DeleteCartSerializer
  renderer_classes = [UserRenderer]
  def post(self,request,id):
    try:
      user = User.objects.filter(id=id)
      cart = Cartitems.objects.get(id=id).delete()
      serializer = ViewCartSerializer(cart)
      return Response({"status": "success", "data": serializer.data}, status = 200)
    except:
      return Response({"status": "Not available"}, status = 400)


class DeleteCartItem(GenericAPIView):
  serializer_class = DeleteCartSerializer
  renderer_classes = [UserRenderer]
  def post(self,request,id):
    user = User.objects.filter(id=id)
    cart = Cartitems.objects.all().delete()
    serializer = DeleteCartSerializer(cart)
    return Response({"status": "success", "data": serializer.data}, status = 200)


class CheckoutView(GenericAPIView):
  serializer_class = CheckoutSerializer
  def post(self,request,id):
    user = User.objects.get(id=id)
    cart_items = Cartitems.objects.filter(user=user)
    # cart = Cartitems.objects.get(id=id)
    dict = {}
    lst = []
    for i,cart in enumerate(cart_items):
      total = cart.quantity * cart.product.price 
      cart_val = Cartitems.objects.filter(user=user).values()
      lst.append(cart_val)
      lst.append(total)
      dict[i] = lst
    return Response({"status": "success","data": lst}, status = 200)


class AllMembership(GenericAPIView):
  serializer_class = MembershipSerializer
  renderer_classes = [UserRenderer]
  def get(self,request):
    membership = Membership.objects.all()
    serializer = MembershipSerializer(membership,many=True)
    return Response({'msg':"success","data":serializer.data}, status = 200)


date = datetime.datetime.now()
end = datetime.timedelta(days=30)

class UserMembershipView(GenericAPIView):
  serializer_class = UserMembershipSerializer
  # renderer_classes = [UserRenderer]
  # permission_classes = [IsAuthenticated]
  def post(self,request,id):
    if not self.request.user.is_authenticated:
      # chck the user is authenticated or not.
      return Response({"msg":"No user Found"})
    user = self.request.user
    membership = Membership.objects.get(id=id)
    member = UserMembership.objects.create(user=user,membership=membership,start_date = date,end_date=end)
    member.save()
    serializer = UserMembershipSerializer(member,many=True)
    return Response({'msg':"success"}, status = 200)
    # token = request.POST['stripeToken']

    # # print(token)
    # stripe.api_key = settings.STRIPE_SECRET_KEY
    # print(stripe.api_key)
    # user = customer = stripe.Customer.create(description='test', source=token)
    # charge = stripe.Charge.create(user=user,membership=membership,currency='inr',source = token,description="membership")