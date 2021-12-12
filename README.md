# JLU_Uims_AutoScore
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

## 待办事项
- [ ] ~~多线程多用户轮训~~不太好解决Session缓存和管理的问题 ~~（我懒）~~
- [ ] ~~多线程识别验证码，当等待时间过长时自动重启线程~~（Python获得线程返回值必须override Thread类，或者可以使用全局变量（list等是线程安全的），但是我不想用，因为这样有可能会对第一个待办事项造成麻烦，而且等待线程返回结果这件事本身就有点**）

## 特别感谢
[@TechCiel](https://github.com/TechCiel) 的 [Reachee](https://github.com/TechCiel/Reachee) 中的大部分代码，故本代码协议与其相同。
