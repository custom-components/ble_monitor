---
layout: default
title: Require active scan
permalink: active_scan_devices
parent: Supported Devices
nav_order: 4
---

{{ site.request_new_devices_msg }}

*NOTE: Properties with a `*` have additional information in the device notes.*

{% assign grouped_by_manufacturer =  site.devices | where:"active_scan", true |sort_natural: "manufacturer"  | group_by: "manufacturer" %}

<span class="fake-h1">Require <a href="configuration_params#active_scan">Active Scan</a> to be enabled</span>
<hr>

{%  for manufacturer  in grouped_by_manufacturer %}

{% assign sorted_items = manufacturer.items | sort_natural: "model" %}

{%  for device  in sorted_items %}
{% include device.html device=device show_mfg_name=true %}
{% endfor %}

{% endfor %}
