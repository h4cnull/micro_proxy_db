apt-get purge proxychains -y
apt-get autoremove -y

echo "Install proxychains4"
git clone https://github.com/rofl0r/proxychains-ng.git
cd proxychains-ng
./configure --prefix=/usr --sysconfdir=/etc
make && make install && make install-config
cd ../

echo "Install proxybroker"
apt-get install python3-pip -y
python3 -m pip install pysocks
python3 -m pip install proxybroker
#python3 -m pip install -U git+https://github.com/constverum/ProxyBroker.git  更新proxybroker

echo "Install microsocks"
git clone https://github.com/rofl0r/microsocks.git
cd microsocks
make
cp microsocks /usr/bin/

echo "Done"
