from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser,Category,Subcategory,myproduct, cart,MyOrder

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('id','username', 'email', 'user_type', 'is_verified', 'is_staff', 'is_superuser')
    list_filter = ('user_type', 'is_verified', 'is_staff')
    search_fields = ('username', 'email')
    ordering = ('username',)

    fieldsets = UserAdmin.fieldsets + (
        ('Extra Info', {'fields': ('user_type', 'is_verified', 'phone', 'address')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','cname','cpic','cdate')


class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('id','category_name','subcategory_name')

admin.site.register(Subcategory,SubcategoryAdmin)


class myproductAdmin(admin.ModelAdmin):
    list_display = ('id','product_category',
                    'subcategory_name', 'product_name','price','discount_price',
                    'product_pic','total_discount','product_quantity','pdate')
    

    def get_category(self, obj):
        return obj.product_category.cname if obj.product_category else '—'
    get_category.short_description = 'Category'

admin.site.register(myproduct,myproductAdmin)



@admin.register(cart)
class cartAdmin(admin.ModelAdmin):
    list_display = ('id','userid','product_name','quantity','price','total_price','product_picture','pw','added_date')


@admin.register(MyOrder)
class MyOrderAdmin(admin.ModelAdmin):
    list_display = ('id','userid','product_name','quantity','price','total_price','product_picture','pw','status','order_date')

