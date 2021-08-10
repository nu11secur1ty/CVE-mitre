# cpiopwn
This is an ACE POC of an integer overflow bug in cpio. This exploit bypasses all binary protections except full RELRO. This exploit uses cpio 2.13 and libc 2.31. Video demo: https://youtu.be/F0yKJhu7Vak 

## Running the exploit

We've provided a Kali Dockerfile to run the exploit. The same exploit should work outside the Docker container, but offsets may be different.

### Instructions
* Build the file
  * `sudo docker build -t cpiopwn .`
* Start the image and mount files
  * `sudo docker run --mount type=bind,source=$(pwd),destination=/cpiopwn -it cpiopwn /bin/bash`
* `cd cpiopwn`
* Run the exploit, which will build a pattern file with `docker_fengshui.py` and call cpio with a large number of command line arguments.
  * `python3 exploit.py`

And that's it! After building the malicious pattern file, a prompt will show up, and it will start processing commands after a little bit of time.

### Notes
The exploit may take about a minute after the prompt appears before it starts responding to commands. We've provided a video of it running to show what should happen.

Additionally, the exploit may only work on computers with at least 12 GB of RAM, as it forces cpio to read gigabytes of input. We had some issues with servers running out of RAM with previous versions of the exploit - the current version has been tested on computers with 12 and 16 GB of RAM, but not smaller.

```
    |\__/,|   (`\
  _.|o o  |_   ) )
-(((---(((--------
```
