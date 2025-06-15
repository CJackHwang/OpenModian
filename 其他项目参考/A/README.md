# 摩点众筹数据爬取

#### 介绍
爬取摩点众筹(https://www.modian.com/) 的数据信息

#### 软件架构
软件架构说明: 使用Jsoup解析页面


#### 安装教程

1.先运行 Test.java ，得到全部的链接地址的 id 存入 id.txt,
    此过程去掉了在预约阶段的数据
  🇺每个链接为： "https://zhongchou.modian.com/item/"+ id +".html"
    示例：https://zhongchou.modian.com/item/3.html


2. id.txt 得到之后，再运行 EveryProject.java，遍历获取每个项目主页上面的信息，
   根据页面上的 众筹成功/众筹结束/看好创意/立即购买支持等信息获取项目的信息，
   获取到的信息重定向输出到 out.txt

3.  将 out.txt 中的数据复制到 excel 中




#### 使用说明

* 使用的语言为 java ，库为 jsoup，参考文档： https://www.open-open.com/jsoup/
* 由于没有ip代理，所以降低了抓取频率，时间设置长一些，访问时间采用随机数
* 抓取过程中可能会存在网络问题导致无法链接，会抛出异常，然后将没有成功的页面再次抓取
* Excel 中的 不明情况 ，我看了情况是 项目主动或者被动终止等情况，不算入成功/失败的众筹项目。

#### 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request


#### 码云特技

1.  使用 Readme\_XXX.md 来支持不同的语言，例如 Readme\_en.md, Readme\_zh.md
2.  码云官方博客 [blog.gitee.com](https://blog.gitee.com)
3.  你可以 [https://gitee.com/explore](https://gitee.com/explore) 这个地址来了解码云上的优秀开源项目
4.  [GVP](https://gitee.com/gvp) 全称是码云最有价值开源项目，是码云综合评定出的优秀开源项目
5.  码云官方提供的使用手册 [https://gitee.com/help](https://gitee.com/help)
6.  码云封面人物是一档用来展示码云会员风采的栏目 [https://gitee.com/gitee-stars/](https://gitee.com/gitee-stars/)
