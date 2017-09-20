YalerTunnel - generic tunneling via the Yaler relay infrastructure

Copyright (c) 2015, Yaler GmbH, Switzerland. All rights reserved.

YalerTunnel makes any service (e.g. a Web server or a SSH daemon) accessible
from the Internet, no matter if the service is behind a firewall, a NAT, or a
mobile network gateway.

If the service is based on HTTP, YalerTunnel is started in server mode,
otherwise in proxy mode. The client either knows HTTP (e.g. a Web browser),
supports HTTP proxies (e.g. PuTTY), or uses a second instance of YalerTunnel
started in client mode to access the tunneled service.


To build the program make sure that you have JDK6 (or later) installed and that
your PATH environment variable includes the JDK's bin directory. Then type:

    javac YalerTunnel.java


Then create a free Yaler account at http://yaler.net/ to get a unique relay
domain for the Yaler instance hosted at try.yaler.net.


Example 1) Running a Web server behind a firewall

Start a Web server listening on port 80 and YalerTunnel in server mode:

    java YalerTunnel server localhost:80 try.yaler.net:80 <relay domain>

E.g., for the relay domain gsiot-ffmq-ttd5 type

    java YalerTunnel server localhost:80 try.yaler.net:80 gsiot-ffmq-ttd5

On the client, open a Web browser and access

    http://try.yaler.net/<relay domain>

In our example, this would be

    http://try.yaler.net/gsiot-ffmq-ttd5


Example 2) Tunneling SSH

Start a SSH daemon listening on port 22 and YalerTunnel in proxy mode:

    java YalerTunnel proxy localhost:22 try.yaler.net:80 <relay domain>

E.g., for the relay domain gsiot-ffmq-ttd5 type

    java YalerTunnel proxy localhost:22 try.yaler.net:80 gsiot-ffmq-ttd5


If your SSH client supports HTTP proxies, configure it to connect via

    http://try.yaler.net/<relay domain>

In our example, this would be

    http://try.yaler.net/gsiot-ffmq-ttd5


Otherwise, start YalerTunnel in client mode

    java YalerTunnel client localhost:10022 try.yaler.net:80 <relay domain>

In our example, this would be

    java YalerTunnel client localhost:10022 try.yaler.net:80 gsiot-ffmq-ttd5

and connect the SSH client to localhost:10022.


Thanks, and please join us at http://yaler.org/

Marc (frei@yaler.net), Thomas (tamberg@yaler.net)