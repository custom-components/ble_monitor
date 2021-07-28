---
layout: default
title: By Broadcasted Property
permalink: by_property
parent: Supported Devices
nav_order: 2
---

{{ site.request_new_devices_msg }}

*NOTE: Properties with a `*` have additional information in the device notes.*

{% comment %}
https://stackoverflow.com/questions/64524362/how-to-get-the-unique-values-of-nested-lists-in-jekyll-data

..but there must be a more performant way to do this.
{% endcomment %}

{% for device in site.devices %}
  {% if  device.broadcasted_properties %}
    {% assign broadcasted_properties = broadcasted_properties | concat: device.broadcasted_properties   %}
  {%  endif %}
{% endfor %}

{% assign broadcasted_properties = broadcasted_properties | uniq | sort_natural %}
{% assign grouped_by_manufacturer =  site.devices | sort_natural: "manufacturer"  | group_by: "manufacturer" %}

{%  for broadcasted_property  in broadcasted_properties %}
#  {{ broadcasted_property }}
<hr>

  {%  for manufacturer  in grouped_by_manufacturer %}
    {% assign sorted_items = manufacturer.items | where_exp:"item", "item.broadcasted_properties contains broadcasted_property" | sort_natural: "model" %}
    {% for device  in sorted_items %}
{% include device.html device=device show_mfg_name=true %}
    {% endfor %}
  {% endfor %}
{% endfor %}
