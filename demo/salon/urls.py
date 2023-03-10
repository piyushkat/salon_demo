from django.urls import path
from salon.views import *


urlpatterns = [
    path('signup',UserRegistrationView.as_view(), name='signup'),
    path('verifyotp',VerifyOtpForEmailVerification.as_view(), name='verifyotp'),
    path('verifyemail',VerifyEmailSecondTime.as_view(), name='verifyemail'),
    path('signin',UserLoginView.as_view(), name='signin'),
    path('profile/<int:id>',UpdateUserProfile.as_view(), name='profileupdate'),
    path('deleteprofile/<int:id>',DeleteUserProfile.as_view(), name='deleteprofile'),
    path('sendemailforpassword',SendPasswordEmailView.as_view(), name='sendemail'),
    path('changepassword',UserChangePasswordView.as_view(), name='changepassword'),
    path('resetpassword/<uid>/<token>',UserPasswordResetView.as_view(), name='resetpassword'),

    path('getallproduct',GetAllProduct.as_view(), name='getallproduct'),
    path('getproductbyid/<int:id>',GetProductById.as_view(), name='getproductbyid'),
    path('product/next/<int:LIMIT>',ProductPaginatioNext.as_view(), name='productpaginationnext'),
    path('product/previous/<int:LIMIT>',ProductPaginationPrevious.as_view(), name='productpaginationprev'),

    path('getproductbycategory/<int:id>', GetProductByCategory.as_view(), name='getproductbycategory'),
    path('getallcategory',GetAllCategory.as_view(), name='getallcategory'),
    path('category/next/<int:LIMIT>',CategoryPaginatioNext.as_view(), name='categorypaginationnext'),
    path('category/previous/<int:LIMIT>',CategoryPaginationPrevious.as_view(), name='categorypaginationprev'),
    path('filter/',FilterProduct.as_view(), name='prev'),
    
    path('addcart/<int:id>',AddProductCart.as_view(), name='addcart'),
    path('viewcart/<int:id>',ViewCartProduct.as_view(), name='viewcart'),
    path('deletecart/<int:id>',DeleteCartItem.as_view(), name='deletecart'),
    path('deletecartbyid/<int:id>',DeleteCartItemById.as_view(), name='deletecartbyid'),
    path('checkoutcart/<int:id>',CheckoutView.as_view(), name='checkoutcart'),
    
    path('membership',AllMembership.as_view(), name='membershipall'),
    path('usermembership/<int:id>',UserMembershipView.as_view(), name='membershipuser'),
    path('getusermembership',GetUserMembership.as_view(), name='getmembershipuser'),
    
    path('reviewrating/<int:id>',ReviewRatingView.as_view(), name='reviewratingview'),
    path('getreviewrating/<int:id>',GetReviewRating.as_view(), name='getreviewratingview'),
    
]