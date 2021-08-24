---
layout: default
title: Supported Devices
permalink: /devices
nav_order: 4
has_children: true
always_show_children: true
---

{{ site.request_new_devices_msg }}

{% comment %}

{% assign grouped_by_manufacturer =  site.devices | sort_natural: "manufacturer"  | group_by: "manufacturer" %}
<table>
<thead>
  <tr>
    <th>Name</th>
    <th>Model</th>
    <th>Description</th>
    <th>Broadcasted properties</th>
    <th>Broadcast Rate</th>
    <th>Requires [active_scan](#active_scan)</th>
    <th>[encryption_key](#encryption_key)</th>
    <th>Custom Firmware</th>
    <th>Notes</th>
  </tr>
</thead>
<tbody>

{%  for manufacturer  in grouped_by_manufacturer %}
{% assign sorted_items = manufacturer.items | sort_natural: "model" %}
{%  for device  in sorted_items %}
<tr>
<td>{{ manufacturer.name }} {{ device.name }}</td>
<td>{{ device.model}}</td>
<td> <img src="{{site.baseurl}}/assets/images/{{ device.image }}" alt="{{device.model}}" /> {{ device.physical_description}}</td>
<td>{{ device.broadcasted_properties }}</td>
<td>{{ device.broadcast_rate}}</td>
<td>{{ device.active_scan}}</td>
<td>{{ device.encryption_key}}</td>
<td>{{ device.custom_firmware  | markdownify }}</td>
<td>{{ device.content | markdownify }}</td>
</tr>
{% endfor %}

{% endfor %}
</tbody>
</table>

{% endcomment %}
