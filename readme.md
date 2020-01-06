1.micro_proxy_db 方便处理、验证proxybroker获取到的代理并存放到数据库中管理，输出格式支持proxychains配置文件。需要安装proxybroker。

```	shell
python3 -m pip install pysocks
python3 -m pip install proxybroker
```

用法。

<img src="pic\1.PNG" />

在历史记录中重新获取代理。

<img src="pic\2.PNG" />

使用--find将调用proxybroker命令获取代理，获取50条，验证后有效代理会少许多，速度略慢，所以加的hisfind功能。

<img src="pic\3.PNG" />

2.目录install_sh_kali 内的脚本适用于在kali中安装proxychains4、proxybroker、microsocks。

microsocks是一个小型socks5代理服务器，再通过proxychains4代理，连接microsocks的代理可以实现动态切换代理。
https://mp.weixin.qq.com/s/01uPc5IbFLs5DUNuGVFt5w
