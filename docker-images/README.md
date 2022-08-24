## 目的

本目录介绍如何制作相关软件的镜像

### ActiveMQ

本文提供了 activemq 镜像构建及运行的方法，更详细的信息请参考我的博客 [构建ActiveMQ镜像并运行](http://www.edulinks.cn/2021/10/21/20211021-make-activemq-docker-image/)。

activemq 文件夹提供了 ActiveMQ 5.16.3 和 ActiveMQ 5.8.0 两个版本构建的配置文件，请根据需要修改 Dockerfile。
<<<<<<< HEAD
因为 github 不建议存放大于 50M 的文件，不支持存放大于 100M 的文件，构建文件夹中用到的三个文件请大家自行下载

* [apache-activemq-5.8.0-bin.tar.gz](http://archive.apache.org/dist/activemq/apache-activemq/5.8.0/apache-activemq-5.8.0-bin.tar.gz), MD5:9984316d59544a23fadd4d5f127f4ebc
* [apache-activemq-5.16.3-bin.tar.gz](http://archive.apache.org/dist/activemq/5.16.3/apache-activemq-5.16.3-bin.tar.gz), MD5: 2cd429148bd86681cf09bf2b1bf7f29d
* jdk-8u144-linux-x64.tar.gz, MD5:2d59a3add1f213cd249a67684d4aeb83
=======
>>>>>>> 3a086fcd8dc0a4c65815a9e42641dfdcd0759fde

修改完成后，在 activemq 目录中执行

```sh
$ docker build -t cocowool/activemq:5.8.0 .
# 通过 docker images 查看是否生成
$ docker images
REPOSITORY                                      TAG                     IMAGE ID       CREATED         SIZE
cocowool/activemq                               5.8.0                   f6bc0084d1a5   12 hours ago    661MB
```