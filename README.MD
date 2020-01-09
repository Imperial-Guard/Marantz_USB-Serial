# Marantz Mediaplayer Component
This is a Custom Component for Home-Assistant (https://home-assistant.io).

You can read and control a Marantz reciever, this is working in combination with a USB to Serial converter

## Installation

### Manual
- Copy directory `marantzusb` to your `<config dir>/custom_components` directory.
- Copy directory `marantz_receiver` to your `<config dir>/deps/lib/python3.7/site-packages` or '<config dir>/lib/python3.7/site-packages/' directory.
- Configure with config below.
- Restart Home-Assistant.

## Usage
To use this component in your installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry

media_player: 
  - platform: marantzusb
    serial_port: /dev/ttyUSB0
    sources:
      2: 'TV'
      3: 'Chromecast'
      G: 'FM'
    soundmode:
      '0' : 'Auto'
      '1' : 'Stereo'
      'T' : 'Source Direct'
      'U' : 'Pure Direct'
```

Configuration variables:

- **serial_port** (*Required*): The USB port on which the USB to Serial can be reached.
- **sources** (*Required*): This is depending on your own set-up.
- **name** (*Optional*): Name of the device. (default = 'Marantz Receiver')
- **min_volume** (*Optional*): Minimal volume of the reciever, will also appear on the volume slider from 0-100% (default = '-71')
- **max_volume** (*Optional*): Maximal volume of the reciever, will also appear on the volume slider from 0-100%  (default = '-1')
