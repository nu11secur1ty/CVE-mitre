# Exploit for WebSocket Vulnerability in Apache Tomcat (CVE-2020-13935)

In the corresponding [blog post](https://blog.redteam-pentesting.de/2020/websocket-vulnerability-tomcat/)
the analysis and exploitation of the vulnerability is explained in detail.

## Usage

Clone the repository, then build the `tcdos` binary. Run the program as follows to test
whether a particular WebSocket endpoint is vulnerable:

```
$ git clone https://github.com/RedTeamPentesting/CVE-2020-13935
$ cd CVE-2020-13935
$ go build
$ ./tcdos [WebSocket endpoint]
```
