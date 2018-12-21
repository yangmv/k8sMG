FROM centos:7
# 设置编码
ENV LANG en_US.UTF-8

# 同步时间
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 1. 安装基本依赖
RUN yum update -y && yum install epel-release -y && yum update -y && yum install wget unzip epel-release nginx  xz gcc automake zlib-devel openssl-devel supervisor net-tools groupinstall development  libxslt-devel libxml2-devel libcurl-devel git -y

# 2. 准备python
RUN wget https://www.python.org/ftp/python/3.6.6/Python-3.6.6.tar.xz
RUN xz -d Python-3.6.6.tar.xz && tar xvf Python-3.6.6.tar && cd Python-3.6.6 && ./configure && make && make install


# 3. 复制代码
RUN mkdir -p /var/www/
ADD . /var/www/k8sMG/
#WORKDIR /var/www/k8sMG/

# 4. 安装pip依赖
RUN pip3 install --user --upgrade pip
RUN pip3 install -r /var/www/k8sMG/requirements.txt

# 5. 数据初始化
RUN python3 /var/www/k8sMG/db_sync.py

# 6. 日志
VOLUME /var/log/

# 7. 准备文件
COPY docs/supervisor_k8s.conf  /etc/supervisord.conf
COPY docs/nginx_k8s.conf /etc/nginx/conf.d/

EXPOSE 80
CMD ["/usr/bin/supervisord"]


##### build测试
# docker build -t k8smg .
# docker run -d -p 8001:80 k8smg:latest
