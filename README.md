# JLU_Uims_AutoScore
自动查成绩，好耶！  
## 使用方法
先更改`main.py`中`username`和`password`字段改成自己的`uims`系统中的用户名和密码，然后修改`m.config`这一行，改成您喜欢的推送方式并按照代码传入正确的字典。  
然后：  
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

## 特别感谢
[@TechCiel](https://github.com/TechCiel) 的 [Reachee](https://github.com/TechCiel/Reachee) 中的部分代码，故本代码协议与其相同。