from django.shortcuts import render,redirect
import  re
from user.models import User,Address
from goods.models import GoodsSKU
from order.models import  OrderInfo,OrderGoods
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.views.generic import View
from django.contrib.auth import authenticate,login,logout
from django.conf import settings
from django.core.mail import send_mail
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from  django.http import HttpResponse
from itsdangerous import SignatureExpired
from celery_tasks.tasks import send_register_active_email
from utils.mixin import LoginRequiredMixin
from django_redis import get_redis_connection
# Create your views here.


#/user/register
def register(request):
    if request.method=='GET':
        return render(request,'register.html')
    else:
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        # 进行数据校验
        print(username, password, email)
        if not all([username, password, email]):
            # 数据不完整

            return render(request, 'register.html', {'errmsg': '数据不完整'})
        # 校验邮箱

        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            print('111')
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})
        print('22222')
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})

        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
            return render(request, 'register.html', {'errmsg': '用户名已存在'})
        except User.DoesNotExist:
            # 进行业务处理:进行用户注册
            user = User.objects.create_user(username, email, password)
            user.is_active = 0
            user.save()
            # 返回应答，跳转到首页
            return redirect(reverse('goods:index'))


def register_handle(request):
    '''进行注册处理'''
    #接受数据
    username = request.POST.get('user_name')
    password =request.POST.get('pwd')
    email = request.POST.get('email')
    allow =request.POST.get('allow')

    #进行数据校验
    print(username,password,email)
    if  not all([username,password,email]):
        #数据不完整

        return render(request,'register.html',{'errmsg':'数据不完整'})
    #校验邮箱

    if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
        print('111')
        return render(request,'register.html',{'errmsg':'邮箱格式不正确'})
    print('22222')
    if allow != 'on':
        return render(request,'register.html',{'errmsg':'请同意协议'})

    #校验用户名是否重复
    try:
        user = User.objects.get(username=username)
        return render(request,'register.html',{'errmsg':'用户名已存在'})
    except User.DoesNotExist:
        #进行业务处理:进行用户注册
        user = User.objects.create_user(username,email,password)
        user.is_active = 0
        user.save()
        #返回应答，跳转到首页
        return redirect(reverse('goods:index'))

class RegisterView(View):

    def get(self,request):
        return render(request,'register.html')

    def post(self,request):
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        # 进行数据校验
        print(username, password, email)
        if not all([username, password, email]):
            # 数据不完整

            return render(request, 'register.html', {'errmsg': '数据不完整'})
        # 校验邮箱

        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            print('111')
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})
        print('22222')
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})

        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
            return render(request, 'register.html', {'errmsg': '用户名已存在'})
        except User.DoesNotExist:
            # 进行业务处理:进行用户注册
            user = User.objects.create_user(username, email, password)
            user.is_active = 0
            user.save()
            #发送激活邮件,包含激活链接:http://127.0.0.1:8000/user/active/id
            #激活链接中需要包含用户的身份信息,并且把身份信息进行加密
            #加密用户的身份信息，生成激活token
            serializer=Serializer(settings.SECRET_KEY,3600)
            info ={'confirm':user.id}
            token = serializer.dumps(info)
            token =token.decode()
            #发邮件
            #celery中发任务，中间人是redis,
            send_register_active_email.delay(email,username,token)
            # 返回应答，跳转到首页
            return redirect(reverse('goods:index'))

class ActiveView(View):

    def get(self,request,token):
        '''进行用户激活'''
        #进行解密，获取要激活的用户信息
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            #获取待激活用户的id
            user_id=info['confirm']
            #进行激活操作
            user = User.objects.get(id=user_id)
            user.is_active =1
            user.save()
            #跳转
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            #激活链接已过期
            return HttpResponse('激活链接已过期')


class LoginView(View):
    def get(self,request):
        '''显示登录页面'''
        #判断是否记住了用户名
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked ='checked'
        else:
            username =''
            checked=''
        return render(request,'login.html',{'username':username,'checked':checked})

    def post(self,request):
        #接受数据
        username =request.POST.get('username')
        password =request.POST.get('pwd')
        print(username,password)
        #校验数据
        if not all([username,password]):
            return render(request,'login.html',{'errmsg':'数据不完整'})
        #业务处理
        user =authenticate(username=username,password=password)
        print(user)
        if user is not None:
            if user.is_active:
                login(request,user)

                #判断是否需要记住用户名
                remember = request.POST.get('remember')
                #获取登录后所要跳转的地址,默认跳转到首页
                next_url=request.GET.get('next',reverse('goods:index'))
                response = redirect(next_url)
                if remember =='on':
                    #记住用户名
                    response.set_cookie('username',username,max_age=7*24*3600)
                else:
                    response.delete_cookie('username')
                #跳转到首页
                return response
            else:
                return render(request,'login.html',{'errmsg':'账户未激活'})
        else:
            return render(request,'login.html',{'errmsg':'用户名或密码错误'})
    #/user

class LogoutView(View):
    '''退出登录'''
    def get(self,request):
        '''退出登录'''
        #清除用户的session信息
        logout(request)
        #跳转到首页
        return redirect(reverse('goods:index'))

class UserInfoView(LoginRequiredMixin,View):
    '''用户中文-信息页'''
    def get(self,request):
        #如果用户未登录，request.user是anonymousUser类的一个实例
        #如果登录了，request.user是User类的一个实例。
        #user.is_authenticated() 判断登录
        #除了自定义给模板文件传递的模板变量之外，django框架会把request.user也传给模板文件

        #获取用户信息
        user =request.user
        address = Address.objects.get_default_address(user)

        #获取用户的历史浏览记录
        # from redis import StrictRedis
        #st=StrictRedis(host='192.168.9.128',port=6379,db=9)
        con =get_redis_connection('default')
        history_key='history_%d'%user.id

        #获取用户最新浏览的5个记录
        sku_ids=con.lrange(history_key,0,4)

        #从数据库中查询用户浏览的商品具体信息
        goods_li=[]
        for id in sku_ids:
            goods = GoodsSKU.objects.get(id=id)
            goods_li.append(goods)

        context ={'page':'user','address':address,'goods_li':goods_li}
        #获取用户的浏览记录
        return render(request,'user_center_info.html',context)

#/user/order
class UserOrderView(LoginRequiredMixin,View):
    '''用户中文-订单页'''
    def get(self, request,page):

        #获取用户的订单信息
        user =request.user
        orders=OrderInfo.objects.filter(user=user).order_by('-create_time')
        #遍历获取订单商品的信息
        for order in orders:
            #根据order_id查寻订单商品信息
            order_skus = OrderGoods.objects.filter(order_id=order.order_id)
            #遍历order_skus 计算商品的小计
            for order_sku in order_skus:
                amount=order_sku.count * order_sku.price
                #动态给order_sku增加属性amount
                order_sku.amount =amount
            #动态给order增加属性，保存订单商品的信息
            order.order_skus =order_skus
            #动态给order增加属性，保存订单状态标题
            order.status_name =OrderInfo.ORDER_STATUS[order.order_status]

        #分页
        paginator =Paginator(orders,1)
        # 获取第page页的内容
        try:
            page = int(page)
        except Exception as e:
            page = 1
        if page > paginator.num_pages:
            page = 1
        # 获取第page页的数据
        order_page = paginator.page(page)
        # 进行页码控制，页面上最多显示5个页码
        # 考虑前三页或最后三页问题,总数小于5
        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1, num_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages - 4, num_pages + 1)
        else:
            pages = range(page - 2, page + 3)

        #组织上下文
        context ={'order_page':order_page,'pages':pages,'page':'order'}
        #处理页面
        return render(request, 'user_center_order.html',context)
  #/user/address
class AddressView(LoginRequiredMixin,View):
    '''用户中文-地址页'''
    def get(self,request):

        #获取用户的默认收货地址
        # 获取登录用户
        user = request.user
        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     address = None
        address = Address.objects.get_default_address(user)
        return render(request, 'user_center_site.html',{'page':'address','address':address})

    def post(self,request):
        '''地址的添加'''
        #接收数据
        receiver=request.POST.get('receiver')
        addr=request.POST.get('addr')
        zip_code=request.POST.get('zip_code')
        phone =request.POST.get('phone')
        #校验数据
        print('1111')
        if not  all([receiver,addr,phone]):
            return render(request,'user_center_site.html',{'errmsg':'数据不完整'})
        print('2222')
        if not re.match(r'^1[3|4|5|7|8][0-9]{9}$',phone):
            return render(request,'user_center_site.html',{'errmsg':'手机号码不完整'})
        #业务处理
        #如果用户以存在默认收货地址，添加的地址不作为默认收货地址，否则作为默认收货地址
        #获取登录用户
        print('3333')
        user = request.user
        address = Address.objects.get_default_address(user)
        if address:
            is_default =False
        else:
            is_default =True
        #添加地址
        Address.objects.create(user=user,receiver=receiver,addr=addr,zip_code=zip_code,phone=phone,is_default=is_default)

        #返回应答,刷新地址页面
        return redirect(reverse('user:address'))