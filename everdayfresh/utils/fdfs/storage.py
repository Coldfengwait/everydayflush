from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.conf import settings
class FDFSStorage(Storage):
    '''fast dfs 文件存储系统'''
    def _open(self,name,mode='rb'):
        '''打开文件时使用'''
        pass

    def _save(self,name,content):
        '''保存文件时使用'''
        #name为上传的文件名
        #content：包含上传文件内容的File对象

        #创建一个Fdfs_client对象
        client=Fdfs_client(settings.FDFS_CLIENT_CONF)

        #上传文件到fast dfs系统中
        res=client.upload_by_buffer(content.read())
        # return dict
        # {
        #     'Group name': group_name,
        #     'Remote file_id': remote_file_id,
        #     'Status': 'Upload successed.',
        #     'Local file name': '',
        #     'Uploaded size': upload_size,
        #     'Storage IP': storage_ip
        # } if success else None
        if res == None:
            #上传失败
            raise Exception('上传文件到fast dfs 失败')
        #获取返回的文件ID
        filename = res.get('Remote file_id')

        return filename

    def exists(self, name):
        '''django判断文件名是否可用'''
        return False

    def url(self, name):
        '''返回访问文件的url路径'''
        return settings.FDFS_URL+name