## 目的

本目录介绍如何制作相关软件的镜像

### ActiveMQ

本文提供了 activemq 镜像构建及运行的方法，更详细的信息请参考我的博客 [构建ActiveMQ镜像并运行](http://www.edulinks.cn/2021/10/21/20211021-make-activemq-docker-image/)。

activemq 文件夹提供了 ActiveMQ 5.16.3 和 ActiveMQ 5.8.0 两个版本构建的配置文件，请根据需要修改 Dockerfile。

修改完成后，在 activemq 目录中执行

```sh
$ docker build -t cocowool/activemq:5.8.0 .
# 通过 docker images 查看是否生成
$ docker images
REPOSITORY                                      TAG                     IMAGE ID       CREATED         SIZE
cocowool/activemq                               5.8.0                   f6bc0084d1a5   12 hours ago    661MB
```