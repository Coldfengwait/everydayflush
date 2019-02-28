from celery import Celery


from django.core.mail import send_mail
from everdayfresh import settings
from django.template import loader,RequestContext
from goods.models import GoodsType,IndexGoodsBanner,IndexPromotionBanner,IndexTtpeGoodsBanner
from django_redis import get_redis_connection
import  os

#创建一个Celery类的实例对象
app=Celery('celery_tasks.tasks',broker='redis://192.168.9.128:6379/8')

#定义任务函数
@app.task
def send_register_active_email(to_email,username,token):
    '''发送激活邮件'''
    #组织邮件信息
    subject = '京东生鲜欢迎信息'
    message = ''
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    html_message = "<h1>%s,欢迎您成为京东生鲜注册会员</h1>请点击下面链接激活您的账户<br/><a href='http://192.168.9.128:8000/user/active/%s'>" \
                   "http://192.168.9.128:8000/user/active/%s</a>" % (username, token, token)
    send_mail(subject, message, sender, receiver, html_message=html_message)

@app.task
def generate_static_index_html():
    # 获取商品的种类信息
    types = GoodsType.objects.all()

    # 获取首页轮播商品信息
    goods_banners = IndexGoodsBanner.objects.all().order_by('index')
    # 获取首页促销活动信息
    promption_banners = IndexPromotionBanner.objects.all().order_by('index')
    # 获取首页分类商品展示信息
    for type in types:
        # 获取type种类首页分类商品的图片展示信息
        image_banners = IndexTtpeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')

        title_banners = IndexTtpeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')
        type.image_banners = image_banners
        type.title_banners = title_banners


    context = {'types': types, 'goods_banners': goods_banners, 'promption_banners': promption_banners,
               }

    print('context的数据为：',context)
    #使用模板
    #1,加载模板文件
    template = loader.get_template('static_index.html')
    #2.模板渲染
    static_index_html=template.render(context)
    print(static_index_html)
    #生成首页对应静态文件
    save_path=os.path.join(settings.BASE_DIR,'static/index.html')
    with open(save_path,'w') as f:
        f.write(static_index_html)
