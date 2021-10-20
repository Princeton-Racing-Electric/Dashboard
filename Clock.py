# Instructions for enabling the hardware clock:
# 1. In a terminal run `sudo raspi-conifg`
# 2. Select option 5 "Interfacing options"
# 3. Select option P5 "I2C"
# 4. For "Would you like the ARM I2C interface to be enabled?" select "Yes"
# 5. Press enter to select "OK"
# 6. Select "Finish"
# 7. If you have `vim` installed (which I recommend over `nano`), `sudo vim /boot/config.txt` file and add this line to your file: `dtoverlay=i2c-rtc,ds1307`.
# 8. Disable the fake hardware clock. We need to do this so that the fake hwclock doesn't interfere with the real hwclock.
# ```
# sudo apt-get -y remove fake-hwclock
# sudo update-rc.d -f fake-hwclock remove
# ```
# 9. With `fake-hwclock` off (or rather, uninstalled), you can start the original hardware clock script. `sudo vim /lib/udev/hwclock-set` and comment out these three lines
# ```
# if [ -e /run/systemd/system ] ; then
# exit 0
# fi
# ```
# This will go to the next section, however, since `/run/udev/hwclock-set` does not exist yet, it will likely go to the next section and load `/etc/default/rcS` which does, and later in the script load `/etc/default/hwclock` which also exists. In the end, this script may create `/run/ude/hwclock-set`. Save your changes.
# 10. Reboot your Pi (`sudo reboot`)
# 11. Check `dmesg` to make sure the module loaded. If you use `dmesg|grep rtc` you should see something like this.
# ```
# [ 3.351935] rtc-ds1307 1-0068: SET TIME!
# [ 3.356747] rtc-ds1307 1-0068: rtc core: registered ds1307 as rtc0
# [ 3.356793] rtc-ds1307 1-0068: 56 bytes nvram
# ```
# The first time around, you will see that first line "SET TIME!" It's basically a warning to set your clock which is what the next step does.
# 12. Finally, set the hardware clock to the system time using `sudo hwclock -w`. You can view and compare the system time (generally called using `date`) against the time set on the hardware clock by using `date && sudo hwclock -r` as follows.
# ```
# pi@raspberrypi:~ $ sudo hwclock -w
# pi@raspberrypi:~ $ date && sudo hwclock -r
# Tue Apr 25 10:36:14 CDT 2017
# Tue 25 Apr 2017 10:36:15 AM CDT -0.628166 seconds
# pi@raspberrypi:~ $
# ```