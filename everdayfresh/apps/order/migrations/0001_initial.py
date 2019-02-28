# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OrderGoods',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(verbose_name='删除标记', default=False)),
                ('count', models.IntegerField(verbose_name='商品数目', default=1)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='订单总金额')),
                ('comment', models.CharField(verbose_name='评论', max_length=256)),
            ],
            options={
                'verbose_name_plural': '订单商品',
                'db_table': 'db_order_goods',
                'verbose_name': '订单商品',
            },
        ),
        migrations.CreateModel(
            name='OrderInfo',
            fields=[
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(verbose_name='删除标记', default=False)),
                ('order_id', models.CharField(primary_key=True, serialize=False, verbose_name='订单编号', max_length=128)),
                ('pay_method', models.SmallIntegerField(default=3, verbose_name='支付方式', choices=[(1, '货到付款'), (2, '微信支付'), (3, '支付宝'), (4, '银联支付')])),
                ('total_count', models.IntegerField(verbose_name='商品数量', default=1)),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='订单总金额 ')),
                ('transit_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='运费')),
                ('order_status', models.SmallIntegerField(default=1, verbose_name='订单状态', choices=[(1, '待支付'), (2, '待发货'), (3, '待收货'), (4, '待评价'), (5, '已完成')])),
                ('trade_no', models.CharField(verbose_name='支付编号', max_length=128)),
            ],
            options={
                'verbose_name_plural': '订单',
                'db_table': 'df_order_info',
                'verbose_name': '订单',
            },
        ),
    ]
