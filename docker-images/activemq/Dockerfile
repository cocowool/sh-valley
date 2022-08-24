FROM centos

MAINTAINER cocowool@qq.com

ADD jdk-8u144-linux-x64.tar.gz /usr/local
#ADD apache-activemq-5.16.3-bin.tar.gz /usr/local
ADD apache-activemq-5.8.0-bin.tar.gz /usr/local
#ADD jetty.xml /usr/local/apache-activemq-5.16.3/conf/jetty.xml
ADD jetty.xml /usr/local/apache-activemq-5.8.0/conf/jetty-5.8.0.xml
# ADD start.sh /usr/local

WORKDIR /usr/local

ENV JAVA_HOME /usr/local/jdk1.8.0_144
#ENV ACTIVEMQ_HOME /usr/local/apache-activemq-5.16.3
ENV ACTIVEMQ_HOME /usr/local/apache-activemq-5.8.0
ENV PATH $JAVA_HOME/bin:$PATH:$ACTIVEMQ_HOME/bin
ENV CLASSPATH .:$JAVA_HOME/lib

EXPOSE 8161/tcp
EXPOSE 5672/tcp
EXPOSE 61612/tcp
EXPOSE 61613/tcp
EXPOSE 61614/tcp
EXPOSE 61616/tcp
EXPOSE 1883/tcp

# ENTRYPOINT ["sh","/usr/local/apache-activemq-5.16.3/bin/activemq start"]
#CMD [ "/usr/local/apache-activemq-5.16.3/bin/activemq", "console" ]
CMD [ "/usr/local/apache-activemq-5.8.0/bin/activemq", "console" ]
