#!/bin/bash
echo "Available serial ports:"
ls -la /dev/tty* 2>/dev/null | grep -E "(ACM|USB)"
echo ""
echo "USB devices:"
lsusb
echo ""
echo "Recent kernel messages:"
dmesg | tail -10
