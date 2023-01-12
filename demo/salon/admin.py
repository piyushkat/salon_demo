from django.contrib import admin
from salon.models import *
from import_export.admin import ImportExportModelAdmin



class ViewAdmin(ImportExportModelAdmin):
    list_display = ('Medicine','Healthcare','Dosage')
admin.site.register(ImportExport,ViewAdmin)


# Register your models here.
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'auth_token', 'is_verified',
                    'is_admin', 'created_at')

admin.site.register(Profile, ProfileAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'image', 'quantity',
                    'price', 'price_before_disc', 'in_stock', 'status', 'category')
    readonly_fields = ('price', 'price_before_disc', 'in_stock', 'status')


admin.site.register(Product, ProductAdmin)

class CategoryAdmin(admin.ModelAdmin):

    list_display = ('name', 'image')
admin.site.register(Category,CategoryAdmin)


class ReviewRatingAdmin(admin.ModelAdmin):
    list_display = ('user','products','review','ratings','created_at')
admin.site.register(ReviewRating,ReviewRatingAdmin)


class CartItemsAdmin(admin.ModelAdmin):
    list_display = ('id','user','product','quantity')
admin.site.register(Cartitems,CartItemsAdmin)


class CheckoutAdmin(admin.ModelAdmin):
    list_display = ('user','cart','quantity','created_at','updated_at')
admin.site.register(CheckoutCart,CheckoutAdmin)


class MembershipAdmin(admin.ModelAdmin):
    list_display = ('slug','membership_type','price')
admin.site.register(Membership,MembershipAdmin)


class UserMembershipAdmin(admin.ModelAdmin):
    list_display = ('user','membership','active')
admin.site.register(UserMembership,UserMembershipAdmin)


# class SubscriptionAdmin(admin.ModelAdmin):
#     list_display = ('user_membership','active')
# admin.site.register(Subscription,SubscriptionAdmin)
