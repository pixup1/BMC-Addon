# Blender Motion Control - Addon

A Blender addon (or extension) that allows the motion of android devices to control objects in a scene, in real time.

Requires an Android device with [BMC - App](https://github.com/pixup1/BMC-App) installed.

## Installation

- Download this repo as a ZIP file;
- In Blender, go to Edit -> Settings -> Add-ons -> Install from Disk... and pick the file you just downloaded.

## Usage

This addon starts a UDP server in a background thread to communicate with mobile devices. This means that you will need to **open a port** in your firewall for incoming UDP connections. By default, this port is 34198. [Here](https://www.wikihow.com/Open-Ports) is a guide to opening ports on most operating systems.

Upon installing the addon, a new "Motion Control" panel will be added to the **right of the viewport**.

### QR Code

This is a QR Code which can be scanned from the app to connect to the host, if it is on the **same network** as the Android device.

Below it is an address that can be input manually if the device lacks a working camera.

### Server Settings

In this tab, the **network interface** used by the addon can be set (if your computer has several). The **port** used for the connection can also be set.

### Connected devices

It is in this tab that the connected devices can be **bound to objects** in the scene. Several devices can be connected and control different objects simultaneously. When a new device is connected, it will automatically be bound to whatever object is currently selected.

There are also controls for how **location** and **rotation** data are applied to the object. There are three modes :
- Replace : The data simply **overwrites** whatever was there before;
- Add : The data is **added** to the original location/rotation of the object;
- Off : The data is **discarded** and does nothing.

Finally, there is a "**Location Scale**" slider, which can be useful for scenes that do not have a uniform scale or simply to control objects of different sizes. A setting of 1 converts one real-life meter to one Blender meter.

### General advice

To "record" the data sent from mobile devices, simply enable the **Auto Keying** toggle in the Blender timeline. Then, as you play through the animation of your scene, simply move your device and its motion will be "baked" onto the object it's bound to.

Then, when playing back recorded data, don't forget to hit the "Mute Data" switch in the app, so the animation and real-time motion aren't fighting.

## License

This addon is licensed under GPL (see [LICENSE.md](LICENSE.md)), but includes a BSD-licensed package ([qrcode](https://pypi.org/project/qrcode/)) and an MIT-licensed package ([ifaddr](https://pypi.org/project/ifaddr)) as wheels.