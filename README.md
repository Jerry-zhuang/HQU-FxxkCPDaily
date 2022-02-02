<!--
 * @Descripttion: 
 * @version: 
 * @Author: A1ertx5s
 * @Date: 2022-02-03 00:38:15
 * @LastEditors: sA1ertx5s
 * @LastEditTime: 2022-02-03 00:55:58
-->
# HQU专属今日校园打卡

华侨大学今日校园打卡程序，目前只针对计算机学院进行测试，其他学院大概率也是可行的。

## 使用方法

### 填写信息

打开isHealth.py, 有一个模板，将所需信息进行填写。

```python
users = [
    {
        "username": "1925104045",   # 此处填写你的学号
        "lon": "118.899015",    # 此处需要填写经度
        "lat": "25.136278",     # 此处需要填写纬度
        "signVersion": "first_v3",
        "calVersion": "firstv",
        "schoolName": "华侨大学",
        "password": "xxxxxxxx",     # 此处填写你的密码
        "address": "你的地址"       # 此处填写你的地址
    },
    ]
```

如果需要多用户，则在users列表种再添加一个。

如下：

```python
users = [
    {
        "username": "1925104045",   # 此处填写你的学号
        "lon": "118.899015",    # 此处需要填写经度
        "lat": "25.136278",     # 此处需要填写纬度
        "signVersion": "first_v3",
        "calVersion": "firstv",
        "schoolName": "华侨大学",
        "password": "xxxxxxxx",     # 此处填写你的密码
        "address": "你的地址"       # 此处填写你的地址
    },
    {
        "username": "1925104045",   # 此处填写你的学号
        "lon": "118.899015",    # 此处需要填写经度
        "lat": "25.136278",     # 此处需要填写纬度
        "signVersion": "first_v3",
        "calVersion": "firstv",
        "schoolName": "华侨大学",
        "password": "xxxxxxxx",     # 此处填写你的密码
        "address": "你的地址"       # 此处填写你的地址
    },
    ]
```

### 自动打卡

此处两种系统

#### Windows

参考下面

https://blog.csdn.net/Artificial_idiots/article/details/108570387

#### Linux

