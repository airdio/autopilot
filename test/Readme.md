nosetests <file>:<Test_Case>.<test_method>


Module:
nosetests tests.test_integration:IntegrationTests.test_user_search_returns_users

Vargarnt Cloud Images:
https://cloud-images.ubuntu.com/vagrant/


DOCKER:
--------
HOST OS: 13.10 or 13.04 (we need kernel 3.8+)
Use this link to install docker
https://www.digitalocean.com/community/articles/how-to-install-and-use-docker-getting-started

http://txt.fliglio.com/2013/11/creating-a-mysql-docker-container/

echo "mysql-server-5.5 mysql-server/root_password password root" | debconf-set-selections
echo "mysql-server-5.5 mysql-server/root_password_again password root" | debconf-set-selections
apt-get -y install mysql-server-5.5


repo:
      autopilot:
          stack:
            role1:
            role2:
            role4:
                cookbooks
                setup.sh


root_dir/
root_dir/meta