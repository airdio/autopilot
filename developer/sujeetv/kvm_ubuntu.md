==Setup networking==
‘(svm|vmx)’ /proc/cpuinfo

sudo apt-get install qemu-kvm libvirt-bin bridge-utils virt-manager
sudo adduser name libvirtd
newgrp libvirtd
virsh -c qemu:///system list

==Setup a bridge==
https://help.ubuntu.com/community/KVM/Networking

==Managing a VM==
https://help.ubuntu.com/community/KVM/Managing

==Cloning a VM===
http://linux.die.net/man/1/virt-clone

Interesting writeup:
http://www.dedoimedo.com/computers/kvm-clone.html


