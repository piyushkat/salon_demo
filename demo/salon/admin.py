from django.contrib import admin
from salon.models import *

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


# class CardAdmin(admin.ModelAdmin):
#     list_display = ('user','product','quantity')
# admin.site.register(Cart,CardAdmin)




class ReviewRatingAdmin(admin.ModelAdmin):
    list_display = ('review','ratings')
admin.site.register(ReviewRating,ReviewRatingAdmin)


# class CartAdmin(admin.ModelAdmin):
#     list_display = ('user','created_at','updated_at')
# admin.site.register(Cart,CartAdmin)



class CartItemsAdmin(admin.ModelAdmin):
    list_display = ('id','product','quantity')
admin.site.register(Cartitems,CartItemsAdmin)