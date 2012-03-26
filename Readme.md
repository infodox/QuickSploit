QuickSploit
===========

Hacked up tool for autopwn goodness.

Quicksploit attempts to hit any windows box on a given subnet with
(ms03_026_dcom and ms08_067_netapi)

This ran at the beggining should get alot of shells to play around with. 
The utility itself has functionality that allows you to interact withe
the shells and send commands to all the shells at the same time.
However it simply talks to metasploit via is MSGPACK

Dependencies:

    MsgPack for python3: http://pypi.python.org/pypi/msgpack-python/

    Install:
        
        Untar msgpack-python-0.1.12.tar.gz
        cd msgpack-python-0.1.12
        sudo python3 setup.py install

To Use:

First start msfconsole:

    ./msfconsole

Then enable the msgpack api plugin:
    
    load msgrpc Pass=abc123 ServerType=Web

    *Note if you changed the password please update the source in QuickSploit.py*

Finally start quicksploit:
	
    python3 QuickSploit.py

Use the help menu from there but since you are here for one thing only.

do:

    quicksploit 192.168.subnetyouwant.starthostnumber

It will then iterate from your specified starthostnumber to 255..
