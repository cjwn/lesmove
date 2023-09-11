# lesmove
a tool for sync files using portable storage device


#### 使用说明
目前还在开发中....


* 运行方法
```
>python /main.py "需要同步本地文件夹"    #扫描这个文件夹，在数据库中做记录
>python /main.py "更新的文件夹" update  #扫描这个文件夹，更新数据库，将一样的文件在数据库中做标记，没有的加进来
```
TODO：产出一个要更新的文件报告，根据报告（或者自动）将文件拷贝到指定位置（也可以做好记录，再实现向本地文件直接同步）
问题：更新数据库时写入极慢
