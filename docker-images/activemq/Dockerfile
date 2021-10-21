FROME centos

MAINTAINER cocowool@qq.com

ADD jdk-8u144-linux-x64.tar.gz /usr/local
ADD apache-activemq-5.15.10-bin.tar.gz /usr/local
ADD start.sh /usr/local

WORKDIR /usr/local

ENV JAVA_HOME /sr/local/jdk1.8.0_144
ENV ACTIVEMQ_HOME /usr/local/apache-activemq-5.15.10
ENV PATH $JAVA_HOME/bin:$PATH:$ACTIVEMQ_HOME/bin
ENV CLASSPATH .:$JAVA_HOME/lib

EXPOSE 61616 8161

ENTRYPOINT ["sh","start.sh"]
