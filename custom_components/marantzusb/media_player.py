"""
Support for interfacing with Marantz receivers through RS-232.

For more details about this platform, please refer to the documentation at

"""
import logging

import voluptuous as vol

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    PLATFORM_SCHEMA)
from homeassistant.components.media_player import MediaPlayerEntityFeature

from homeassistant.const import (
    CONF_NAME, STATE_OFF, STATE_ON)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'Marantz Receiver'
DEFAULT_MIN_VOLUME = -71
DEFAULT_MAX_VOLUME = -1

SUPPORT_MARANTZ = MediaPlayerEntityFeature.VOLUME_SET | MediaPlayerEntityFeature.VOLUME_MUTE | \
    MediaPlayerEntityFeature.TURN_ON | MediaPlayerEntityFeature.TURN_OFF | MediaPlayerEntityFeature.VOLUME_STEP | \
    MediaPlayerEntityFeature.SELECT_SOURCE | MediaPlayerEntityFeature.SELECT_SOUND_MODE 

CONF_SERIAL_PORT = 'serial_port'
CONF_MIN_VOLUME = 'min_volume'
CONF_MAX_VOLUME = 'max_volume'
CONF_SOURCE_DICT = 'sources'
CONF_SOUNDMODE_DICT = 'soundmode'
CONF_UNIQUE_ID = 'unique_id'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_SERIAL_PORT): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_MIN_VOLUME, default=DEFAULT_MIN_VOLUME): int,
    vol.Optional(CONF_MAX_VOLUME, default=DEFAULT_MAX_VOLUME): int,
    vol.Optional(CONF_SOURCE_DICT, default={}): {cv.string: cv.string},
    vol.Optional(CONF_SOUNDMODE_DICT, default={}): {cv.string: cv.string},
    vol.Optional(CONF_UNIQUE_ID, default=''): cv.string,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Marantz platform."""
    from marantz_receiver import MarantzReceiver
    add_devices([Marantz(
        config.get(CONF_NAME),
        MarantzReceiver(config.get(CONF_SERIAL_PORT)),
        config.get(CONF_MIN_VOLUME),
        config.get(CONF_MAX_VOLUME),
        config.get(CONF_SOURCE_DICT),
        config.get(CONF_SOUNDMODE_DICT),
        config.get(CONF_UNIQUE_ID)
    )], True)


class Marantz(MediaPlayerEntity):
    """Representation of a Marantz Receiver."""

    def __init__(self, name, marantz_receiver, min_volume, max_volume,
                 source_dict, sound_mode_dict, unique_id):
        """Initialize the Marantz Receiver device."""
        self._name = name
        self._marantz_receiver = marantz_receiver
        self._min_volume = min_volume
        self._max_volume = max_volume
        self._source_dict = source_dict
        self._sound_mode_dict = sound_mode_dict
        self._reverse_mapping = {value: key for key, value in
                                 self._source_dict.items()}
        self._reverse_mapping_sound_mode = {value: "0{}".format(key) for key, value in
                                 self._sound_mode_dict.items()}
        self._unique_id = unique_id

        self._volume = self._state = self._mute = self._source = None

    def calc_volume(self, decibel):
        """
        Calculate the volume given the decibel.

        Return the volume (0..1).
        """
        return abs(self._min_volume - decibel) / abs(
            self._min_volume - self._max_volume)

    def calc_db(self, volume):
        """
        Calculate the decibel given the volume.

        Return the dB.
        """
        return self._min_volume + round(
            abs(self._min_volume - self._max_volume) * volume)

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    def update(self):
        """Retrieve latest state."""
        if self._marantz_receiver.main_power(':', '?') == '1':
            self._state = STATE_OFF
        else:
            self._state = STATE_ON

        if self._marantz_receiver.main_mute(':', '?') == '1':
            self._mute = False
        else:
            self._mute = True

        volume_result = self._marantz_receiver.main_volume(':', '?')
        if (volume_result != None):
            self._volume = self.calc_volume(volume_result)
            
        self._source = self._source_dict.get(
            self._marantz_receiver.main_source(':', '?'))
        self._sound_mode = self._sound_mode_dict.get(
            self._marantz_receiver.main_sound_mode(':', '?'))

    @property
    def volume_level(self):
        """Volume level of the media player (0..1)."""
        return self._volume

    @property
    def is_volume_muted(self):
        """Boolean if volume is currently muted."""
        return self._mute

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_MARANTZ

    def turn_off(self):
        """Turn the media player off."""
        self._marantz_receiver.main_power(':', '3')

    def turn_on(self):
        """Turn the media player on."""
        self._marantz_receiver.main_power(':', '2')

    def volume_up(self):
        """Volume up the media player."""
        self._marantz_receiver.main_volume(':', '1')

    def volume_down(self):
        """Volume down the media player."""
        self._marantz_receiver.main_volume(':', '2')

    def set_volume_level(self, volume):
        """Set volume level, range 0..1."""
        vol_calc = '0' + str(self.calc_db(volume))
        self._marantz_receiver.main_volume(':', vol_calc)

    def select_source(self, source):
        """Select input source."""
        self._marantz_receiver.main_source(':', self._reverse_mapping.get(source))

    def select_sound_mode(self, sound_mode):
        """Select sound mode."""
        self._marantz_receiver.main_sound_mode(':', self._reverse_mapping_sound_mode.get(sound_mode))
        
    def mute_volume(self, mute):
        """Mute (true) or unmute (false) media player."""
        if mute:
            self._marantz_receiver.main_mute(':', '2')
        else:
            self._marantz_receiver.main_mute(':', '1')
            
    @property
    def source(self):
        """Name of the current input source."""
        return self._source

    @property
    def sound_mode(self):
        """Name of the current sound_mode."""
        return self._sound_mode

    @property
    def source_list(self):
        """List of available input sources."""
        return sorted(list(self._reverse_mapping.keys()))

    @property
    def sound_mode_list(self):
        """List of available sound_modes."""
        return sorted(list(self._reverse_mapping_sound_mode.keys()))

    @property
    def unique_id(self):
        return self._unique_id

