conkyKeep
=========
[![Code Climate](https://codeclimate.com/github/kunesj/conkyKeep/badges/gpa.svg)](https://codeclimate.com/github/kunesj/conkyKeep)

Show notes from [Google Keep](https://keep.google.com/) on Linux desktop with conky.

![Preview](preview.jpg)

Installation
------------

Install dependencies:

    sudo apt-get install python3 python3-pip python3-pil python3-numpy conky-all
    sudo pip3 install gkeepapi==0.11.2 configparser

Copy and then rename config_user.cfg to ~/.config/conkykeep/config.cfg. You can also create copy in the same folder (as conkyKeep.sh) which has higher priority.

    mkdir -p ~/.config/conkykeep/
    cp config_user.cfg ~/.config/conkykeep/config.cfg

Set correct Google login information inside copied config.cfg.

For more information about settings, note styling, filtering and more, look inside file config_default.cfg.


Usage
-----

Run it with:

    ./conkyKeep.sh start

Stop it with:

    ./conkyKeep.sh stop

Restart it with:

    ./conkyKeep.sh restart


License
-------
GNU GENERAL PUBLIC LICENSE Version 3


Credits
-------
Google login code based on: [http://stackoverflow.com/a/24881998](http://stackoverflow.com/a/24881998)

File conkyKeep.sh is based on: [conkyPress](https://github.com/linuxm0nk3ys/conkyPress) (GPL3)


