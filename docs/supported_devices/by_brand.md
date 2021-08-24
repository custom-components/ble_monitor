---
layout: default
title: By Manufacture
permalink: by_brand
parent: Supported Devices
nav_order: 1
---

{{ site.request_new_devices_msg }}

*NOTE: Properties with a `*` have additional information in the device notes.*

{% assign grouped_by_manufacturer =  site.devices | sort_natural: "manufacturer"  | group_by: "manufacturer" %}

{%  for manufacturer  in grouped_by_manufacturer %}
# {{ manufacturer.name }}
<hr>

{% assign sorted_items = manufacturer.items | sort_natural: "model" %}

{%  for device  in sorted_items %}
{% include device.html device=device show_mfg_name=false %}
{% endfor %}

{% endfor %}
