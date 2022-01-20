# JLU_Uims_AutoScore
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/b1d52177d5ea43928ceda14310284988)](https://www.codacy.com/gh/ForeverOpp/JLU_Uims_AutoScore/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ForeverOpp/JLU_Uims_AutoScore&amp;utm_campaign=Badge_Grade)

自动查成绩，好耶！  
## 使用方法
更改`config.example.ini`中`Default`字段的配置项，然后重命名为`config.ini`。

最后：  
`pip install -r requirements.txt`  
`python3 main.py`  
就可以了，等待着~~挂科~~满绩的消息吧~  

## 树莓派安装Tensorflow 2.4方法
安装方法来源此仓库：[Tensorflow-bin](https://github.com/PINTO0309/Tensorflow-bin)  
```sheel
$ sudo apt-get install -y libhdf5-dev libc-ares-dev libeigen3-dev gcc gfortran python-dev libgfortran5 \
                          libatlas3-base libatlas-base-dev libopenblas-dev libopenblas-base libblas-dev \
                          liblapack-dev cython libatlas-base-dev openmpi-bin libopenmpi-dev python3-dev
$ sudo pip3 install keras_applications==1.0.8 --no-deps
$ sudo pip3 install keras_preprocessing==1.1.0 --no-deps
$ sudo pip3 install h5py==2.9.0
$ sudo pip3 install pybind11
$ pip3 install -U --user six wheel mock
$ wget "https://raw.githubusercontent.com/PINTO0309/Tensorflow-bin/master/tensorflow-2.4.0-cp37-none-linux_armv7l_download.sh"
$ ./tensorflow-2.4.0-cp37-none-linux_armv7l_download.sh
$ sudo pip3 uninstall tensorflow
$ sudo -H pip3 install tensorflow-2.4.0-cp37-none-linux_armv7l.whl

【Required】 Restart the terminal.
```
如果仍旧无法运行，请尝试使用普通用户执行上述步骤。  

## 已知问题
- 若使用VPN登录不稳定，请在`VPNLogin`中加入如下代码：
```python
    headers['Host'] = "vpns.jlu.edu.cn"
    headers['Origin'] = "https://vpns.jlu.edu.cn"
    headers['referer'] = "https://vpns.jlu.edu.cn/do-login?local_login=true"
    jsonHeaders['Host'] = "vpns.jlu.edu.cn"
    jsonHeaders['Origin'] = "https://vpns.jlu.edu.cn"
    jsonHeaders['referer'] = "https://vpns.jlu.edu.cn/do-login?local_login=true"
```
- 由于使用了炼丹来识别验证码，程序占用内存非常大，大约为200M，并且在i5-9400F上占用大概70%的CPU。尝试使用`del`关键字但是并没有用，是tensorflow的问题，~~但是暂时没有很好的解决办法~~可以尝试使用百度OCR等进行识别。
- 炼丹识别验证码有时候会卡住，需要手动重启程序。  
- 自动重新登录时，会发生堆栈错误（没有内存日志所以无法分析是不是内存崩了），推测是识别验证码时，调用识别方法是多线程的，并不会等待线程结束，又由于递归调用，所以会存在~~Stack Overflow~~的问题。  

## 多用户思路
1. 创建会话池池，如果会话池池最大容量小于用户数，就先查完会话池池里的再查剩余用户的并将他们的登录状态存回会话池池
2. 如果 VPN 登录状态下，不支持多用户，则简单轮询，不使用会话池池
3. 配置文件 Section 每个用户独立一个，随便填，但配置项要有 UserName 和 Password，如果 2 成立，最好让每个用户单独有个 VPN 账号，这样即可实现会话池池
4. 多用户状态保存，目前有两种想法：1 存入数据库，2 建立一个文件夹，然后以 Section/UserName 作为文件名。
5. 当然需要在读取配置文件的时候去重（提示即可）
6. 会话池池可以多线程进行操作，只需要设置 Interval 触发即可
7. 不知道上述方法能不能用，因为会话池本来就已经复用 TCP 链接了，这样操作感觉多此一举
8. 如果无法多线程轮询，那么查询速度会很慢，如果用户多可能会造成等待时间大于 Interval 时间，所以要设置一个事件锁，如果时间较长，就跳过下次查询，等查完为止
9. 不行就把项目 Duplicate 几份单独执行
10. 无论如何需要一个批量添加用户的工具，手写配置文件 Section 可不是个好的体验

## 待办事项
- [ ] ~~多线程多用户轮训~~不太好解决Session缓存和管理的问题，原因如上 ~~（我懒）~~
- [ ] ~~多线程识别验证码，当等待时间过长时自动重启线程~~（Python获得线程返回值必须override Thread类，或者可以使用全局变量（list等是线程安全的），但是我不想用，因为这样有可能会对第一个待办事项造成麻烦，而且等待线程返回结果这件事本身就有点**），再者没必要，如果更换专用模型，识别率可以达到 90% 以上，识别 1 次即可
- [ ] 配置文件生成器
- [ ] 更换专用模型，至少也得用谷歌的手写数字预训练模型，目前程序识别失败的原因纯纯是识别成字母了

## 特别感谢
[@TechCiel](https://github.com/TechCiel) 的 [Reachee](https://github.com/TechCiel/Reachee) 中的大部分代码。
