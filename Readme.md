conkyKeep
=========
[![Code Climate](https://codeclimate.com/github/kunesj/conkyKeep/badges/gpa.svg)](https://codeclimate.com/github/kunesj/conkyKeep)

Show notes from [Google Keep](https://keep.google.com/) on Linux desktop with conky.


Installation
------------

Install dependencies: 

    sudo apt-get install python3 python3-pip conky-all
    sudo pip3 install requests beautifulsoup4

Copy and then rename config_default.xml to ~/.config/conkykeep/config.xml. You can also create copy in the same folder (as conkyKeep.sh) which has higher priority.

    mkdir -p ~/.config/conkykeep/
    cp config_default.xml ~/.config/conkykeep/config.xml
    
Set correct Google login information inside copied config.xml.


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
Some parts are based on [conkyPress](https://github.com/linuxm0nk3ys/conkyPress)

Google login code based on: [http://stackoverflow.com/a/24881998](http://stackoverflow.com/a/24881998)
