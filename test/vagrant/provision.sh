#!/bin/sh

yum install -y epel-release
yum install -y xz
yum install -y python-pip

# python 2.7
wget http://python.org/ftp/python/2.7.5/Python-2.7.5.tar.xz -q
tar xf Python-2.7.5.tar.xz
pushd Python-2.7.5
./configure --prefix=/usr/local --enable-unicode=ucs4 --enable-shared LDFLAGS="-Wl,-rpath /usr/local/lib"
make && make altinstall
popd

#virtualenv
pushd /home/vagrant/
pip install virtualenv
virtualenv vtest -p /usr/local/bin/python2.7
chown -R vagrant:vagrant vtest
source vtest/bin/activate

# ap pre-reqs
/bin/sh /home/vagrant/autopilot/setup/install_libs.sh
pip install nose
pip install -r /home/vagrant/autopilot/setup/requirements.txt

popd