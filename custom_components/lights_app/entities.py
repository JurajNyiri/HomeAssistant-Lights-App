from homeassistant.util import slugify
from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.const import CONF_ADDRESS, STATE_UNAVAILABLE
from homeassistant.components.light import LightEntity
from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN


class LightsAppEntity(Entity):
    def __init__(self, hass, config_entry: dict, entryData: dict, name_suffix: str):
        self._hass = hass
        self._address = config_entry.data.get(CONF_ADDRESS)
        self._client = hass.data[DOMAIN][config_entry.entry_id]["connection"]["client"]
        self._service = hass.data[DOMAIN][config_entry.entry_id]["connection"][
            "service"
        ]
        self._entryData = entryData
        self._config_entry = config_entry
        self._enabled = False
        self._name = "Lights App"
        self._name_suffix = name_suffix
        Entity.__init__(self)

    @property
    def name(self) -> str:
        return "{} {}".format(self._name, self._name_suffix)

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, slugify(f"{self._address}_lights_app"))},
            connections={("bluetooth", self._address)},
            name=self._name,
            manufacturer="Lights App",
        )

    @property
    def unique_id(self) -> str:
        id_suffix = "".join(self._name_suffix.split())
        return "{}-{}-{}".format(self._address, self._name, id_suffix).lower()


class LightsAppLightEntity(LightEntity, LightsAppEntity):
    def __init__(self, hass, config_entry: dict, entryData: dict, name_suffix: str):
        LightsAppEntity.__init__(self, hass, config_entry, entryData, name_suffix)
        LightEntity.__init__(self)


class LightsAppSwitchEntity(SwitchEntity, LightsAppEntity):
    def __init__(self, hass, config_entry: dict, entryData: dict, name_suffix: str):
        LightsAppEntity.__init__(self, hass, config_entry, entryData, name_suffix)
        SwitchEntity.__init__(self)
