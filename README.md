# HomeAssistant - Lights App

Custom component that allows control of lights by [Lights App](https://play.google.com/store/apps/details?id=com.novolink.lightapp&hl=en_US)

<p float="left">
  <img src="/img/img2.jpeg" width="200" />
  <img src="/img/img1.jpeg" width="200" /> 
</p>

## Installation

Copy contents of custom_components/lights_app/ to custom_components/lights_app/ in your Home Assistant config folder.

## Installation using HACS

Add this repository as custom repository.

HACS is a community store for Home Assistant. You can install [HACS](https://github.com/custom-components/hacs) and then install Lights App from the HACS store.

## Supported devices

Currently the 48m and the 5.5m variant are supported. If your device does not show up, check the available Bluetooth devices on your phone and add the name to the `SUPPORTED_BLUETOOTH_NAMES` in the `const.py` and please open PR.

## Usage

Integration allows setting brightness, controlling state and all the available modes.

<p float="left">
  <img src="/img/img3.png" width="400" />
</p>

## Have a comment or a suggestion?

Please [open a new issue](https://github.com/JurajNyiri/HomeAssistant-Lights-App/issues/new/choose), or discuss on [Home Assistant: Community Forum](https://community.home-assistant.io/t/custom-component-tapo-cameras-control/231795).

## Thank you

<a href="https://www.buymeacoffee.com/jurajnyiri" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-blue.png" alt="Buy Me A Coffee"  width="150px" ></a>
