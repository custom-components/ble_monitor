---
layout: default
title: Encrypted Advertisements
permalink: encrypted_advertisements
parent: Supported Devices
nav_order: 3
---

{{ site.request_new_devices_msg }}

*NOTE: Properties with a `*` have additional information in the device notes.*

{% assign grouped_by_manufacturer =  site.devices | where_exp: "device", "device.encryption_key" |sort_natural: "manufacturer"  | group_by: "manufacturer" %}


Advertisements for these devices are encrypted, therefore you need to set the key in your configuration, see for instructions
 the [encryption_key](configuration_params#encryption_key) option
 {: .py-5}

<span class="fake-h1">Encrypted Advertisements</span>
<hr>

{%  for manufacturer  in grouped_by_manufacturer %}

{% assign sorted_items = manufacturer.items | sort_natural: "model" %}

{%  for device  in sorted_items %}
{% include device.html device=device show_mfg_name=true %}
{% endfor %}

{% endfor %}
