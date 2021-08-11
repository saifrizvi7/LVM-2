import unittest
import cli
from runner import execute,fio
import subprocess

class Task(unittest.TestCase):
    disk = " ".join(cli.disk_name)
    
    def tearDown(self):
        disk = " ".join(cli.disk_name)
        
        self.vgpath = "/dev/{}/{}".format(cli.vgname,cli.lvname)
        execute("umount /data")
        execute("rmdir /data")
        execute("wipefs -a {}".format(self.vgpath))

        print("Removing the Logical Volume {}".format(cli.lvname))
        execute("lvremove -f {}" .format(cli.vgname), inp="y\n")

        print("Removing the Volume Group {}".format(cli.vgname))
        execute("vgremove {}".format(cli.vgname))
        
        print("Removing the Physical Volume {}".format(Task.disk))
        execute("pvremove {}" .format(disk))


    def test_xlvcreate(self):
        print("Creating Physical Volume {}".format(Task.disk))
        execute("pvcreate {}" .format(Task.disk))

        print("Creating Volume group {}".format(cli.vgname))
        execute("vgcreate {} {}" .format(cli.vgname, Task.disk))

        print("Creating Logical Volume {}" .format(cli.lvname))
        execute("lvcreate --size {} --name {} {}".format(cli.size,cli.lvname,cli.vgname))
        
        self.lvpath = "/dev/{}/{}" .format(cli.vgname, cli.lvname)
        
        print("Creating an {} filesystem on the Logical Volume {}" .format(cli.fs,cli.lvname))
        execute("sudo mkfs -t {} {}" .format(cli.fs, self.lvpath))

        execute("mkdir /data")

        execute("mount {} /data" .format(self.lvpath))
        print("Verifying if the Filesystem is mounted")
        print("Verifying whether IO is successful")
        self.fio_fun = fio("fio --filename={} --direct=1 --size=1G --rw=randrw --bs=4k --ioengine=libaio --iodepth=256 --runtime=5 --numjobs=32 --time_based --group_reporting --name=iops-test-job --allow_mounted_write=1".format(self.lvpath))
        self.fspath = "dev/mapper/{}-{}" .format(cli.vgname, cli.lvname)
        self.outpv = execute("pvdisplay")
        self.outvg = execute("vgdisplay")
        self.output = execute("lvdisplay")
        self.outmnt = execute("findmnt")

        for i in cli.disk_name:
            self.assertRegex(self.outpv,i)

        self.assertRegex(self.outvg,cli.vgname)
        
        self.assertRegex(self.output,cli.lvname)

        self.assertRegex(self.outmnt,self.fspath)
        
        self.assertRegex(self.fio_fun,"Run status")

