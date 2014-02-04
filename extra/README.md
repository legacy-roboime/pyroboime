To use the transmission on a linux with udev copy the rules file:

    cp ./99-vivatx.rules /etc/udev/rules.d/

Restart udev with:

    sudo udevadm trigger

Ref: https://github.com/braiden/python-ant-downloader/issues/30
