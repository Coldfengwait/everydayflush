from django.contrib import admin
from django.core.cache import cache
from goods.models import GoodsType,GoodsSKU,Goods,GoodsImage,IndexGoodsBanner,IndexTtpeGoodsBanner,IndexPromotionBanner
# Register your models here.
class BaseModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        '''新增或更新表中的数据时调用'''
        super().save_model( request,obj, form, change)
        #发出任务，让celery worker 重新生成静态页面
        from celery_tasks.tasks import generate_static_index_html
        generate_static_index_html.delay()
        #清除首页缓存存储
        cache.delete('index_page_data')
    def delete_model(self, request, obj):
        '''删除表中的数据时调用'''
        super(IndexPromotionBannerAdmin, self).delete_model(request, obj)
        # 发出任务，让celery worker 重新生成静态页面
        from celery_tasks.tasks import generate_static_index_html
        generate_static_index_html.delay()
        # 清除首页缓存存储
        cache.delete('index_page_data')

class GoodsTypeAdmin(BaseModelAdmin):
    pass
class GoodsSKUAdmin(BaseModelAdmin):
    pass
class GoodsAdmin(BaseModelAdmin):
    pass
class GoodsImageAdmin(BaseModelAdmin):
    pass
class IndexGoodsBannerAdmin(BaseModelAdmin):
    pass
class IndexTtpeGoodsBannerAdmin(BaseModelAdmin):
    pass
class IndexPromotionBannerAdmin(BaseModelAdmin):
    pass
admin.site.register(GoodsType,GoodsTypeAdmin)
admin.site.register(GoodsSKU,GoodsSKUAdmin)
admin.site.register(Goods,GoodsAdmin)
admin.site.register(GoodsImage,GoodsImageAdmin)
admin.site.register(IndexGoodsBanner,IndexGoodsBannerAdmin)
admin.site.register(IndexTtpeGoodsBanner,IndexTtpeGoodsBannerAdmin)
admin.site.register(IndexPromotionBanner,IndexPromotionBannerAdmin)