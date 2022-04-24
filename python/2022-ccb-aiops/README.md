---
title: 国际 AIOPS 挑战赛参赛实录
date: 2022-04-12 21:42:28
keywords: AIOPS, python, 比赛记录
description: 本文记录参加 2022 年 AIOPS 比赛的学习体会。
---

> 本文在 Python 3 的环境下运行相关代码

2022年 CCF 国际 AIOPS 挑战赛由清华大学联合中国计算机学会（CCF）共同发起，自2018年迄今已经举办四届，今年是第五届。今年首次引入故障分类赛题，以「微服务架构电商系统下故障识别和分类」为赛题，挖掘故障模式、构建分类模型以作用于故障止损场景。比赛将全程在建行云环境下完成，参赛选手需自行设计「异常检测算法」和「故障分类算法」，实现准确高效的故障检测和故障分类。

## 思路

* 消费 Kafka 数据，汇总统计异常值，如返回码不是200的交易请求、业务成功率等，根据异常类型设置不同的阈值
* 当同一时间点异常指标数超过某一阈值时，判断该时间点发生了故障
  * 指标的关联性，考虑 Kendall 方法计算相关系数，如交易量和CPU使用率建立关联关系

## 窍门

关注「智能运维前沿」这个公众号，会有意想不到的收获。

## 数据分析

```sh
$ vim metric_service.csv
1 service,timestamp,rr,sr,mrt,count                                     
2 adservice-grpc,1647702000,100.0,100.0,2.515697674418334,86
3 adservice-grpc,1647702060,100.0,100.0,2.515697674418334,86
4 adservice-grpc,1647702120,100.0,100.0,2.3357142857126227,70
```

几个数据的解释

* rr 表示系统响应率 Response Rate
* sr 表示业务成功率 Success Rage
* mrt 表示平均响应时间 Mean response time
* count 表示交易量



需要做的是流式数据异常检测。

## 关键概念

* 相关分析 Kendall 相关系数

## 使用到的包

* kafka-python
* Pandas
* Numpy
* scipy

## 参考资料

1. [蚂蚁智能运维: 单指标异常检测算法初探](https://segmentfault.com/a/1190000023696934)
2. [使用 Python 进行异常检测](https://www.cnblogs.com/panchuangai/p/13817905.html?ivk_sa=1024320u)
1. [Python 时间戳转换](https://blog.csdn.net/weixin_39524425/article/details/110538364)
1. []()

