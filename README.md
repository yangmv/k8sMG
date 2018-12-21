### K8S发布管理平台
#### 实现方式
-
- 前端：Vue.js + iview
- 后端：Tornado
- 其他组件：K8S + Jenkins

#### 项目功能：
- 项目创建，管理，关联应用
- 应用管理，关联代码仓库
- 发布管理，整个项目发布，单个应用发布，发布审核


### 一键部署
```
docker build -t k8smg .
pip3 install docker-compose
docker-compose up -d
```


### 人工部署
#### 一 安装依赖
```
pip3 install --upgrade pip
pip3 install -r requirements.txt
```

#### 二 配置
- 配置文件 settings.py
- 配置DB,Cache,MQ,Jenkins
```
cp settings_example.py settings.py
```

#### 三 创建表结构
```
python3 models/db_sync.py
```

#### 四 Supervisor
```
cat >> /etc/supervisord.conf <<EOF
[program:k8s_mg]
command=python3 startup.py --service=k8s_mg --port=90%(process_num)02d
process_name=%(program_name)s_%(process_num)02d
numprocs=3
directory=/var/www/k8sMG
user=root
autostart = true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/k8s_mg.log
loglevel=info
logfile_maxbytes=100MB
logfile_backups=3

[program:k8s_task]
command=python3 startup.py --service=k8s_task --port=91%(process_num)02d
process_name=%(program_name)s_%(process_num)02d
numprocs=3
directory=/var/www/k8sMG
user=root
autostart = true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/k8s_task.log
loglevel=info
logfile_maxbytes=100MB
logfile_backups=3

[program:k8s_ws]
command=python3 startup.py --service=k8s_ws --port=92%(process_num)02d
process_name=%(program_name)s_%(process_num)02d
numprocs=
directory=/var/www/k8sMG
user=root
autostart = true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/k8s_ws.log
loglevel=info
logfile_maxbytes=100MB
logfile_backups=3
EOF

supervisorctl update
supervisorctl reload
```


#### 五 Nginx配置
```
upstream  k8s_mg{
    server  127.0.0.1:9000;
    server  127.0.0.1:9001;
    server  127.0.0.1:9002;
}

upstream  k8s_ws{
    server  127.0.0.1:9200;
    server  127.0.0.1:9201;
    server  127.0.0.1:9202;
}

location /v1/k8s/ {
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Scheme $scheme;
        proxy_pass http://k8s_mg;
}

location /v1/k8s-ws/ {
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Scheme $scheme;
        proxy_pass http://k8s_ws;
}

```



### 前台展示
#### 应用管理
![image](https://raw.githubusercontent.com/yangmv/k8sMG/master/images/01.png)

#### 项目管理
![image](https://raw.githubusercontent.com/yangmv/k8sMG/master/images/02.png)

#### 项目创建
![image](https://raw.githubusercontent.com/yangmv/k8sMG/master/images/03.png)

#### 项目发布
![image](https://raw.githubusercontent.com/yangmv/k8sMG/master/images/04.png)

#### 发布详情
![image](https://raw.githubusercontent.com/yangmv/k8sMG/master/images/05.png)

## License

Everything is [GPL v3.0](https://www.gnu.org/licenses/gpl-3.0.html).