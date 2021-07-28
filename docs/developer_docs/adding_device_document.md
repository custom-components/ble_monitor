---
layout: default
title: Documentation on documentation
parent: Technical and development documentation
permalink: documentation
nav_order: 1
---

## Adding a new device

1. Create a markdown file with the extension `.md` in `docs/_devices/`.

2. Add an image of the device and place it under `docs/_assets/images`.

3. Copy and paste the following template into the markdown file.  Fill in the relevant information.

```markdown
---
manufacturer:
name:
model:
image:
physical_description:
broadcasted_properties:
  - EXAMPLE
broadcasted_property_notes:
  - property: EXAMPLE
    note: EXAMPLE
broadcast_rate:
active_scan:
encryption_key:
custom_firmware:
  - name: EXAMPLE
    url: EXAMPLE
notes:
  - EXAMPLE
---

```
* Every instance of *EXAMPLE* is a place filler and is intended to be removed or placed with relevant information.
* While the file ends in md and is treated as markdown, the syntax between the start and end `---` is YAML
  ([explained here](https://github.com/jekyll/jekyll/issues/6188))
* `broadcasted_properties`, `broadcasted_property_notes` and `notes` are arrays.
* `manufacturer`, `name` , `model`, `image` and at least one `broadcasted_properties` are **required**.
* `broadcast_rate`, `active_scan` and `encryption_key` are "truthy" values and will appear for value other than `false` or `nil`.
* `broadcasted_property_notes` is a key/value array intended to provide addition information for individual properties.  `property` must match a value in `broadcasted_properties`.
* `custom_firmware` is a key/value array where `name` is the name of the link and `url` is the url of the firmware.


4.  When the theme is regenerated, the new device should appear in the relative "Supported Devices".

## Local development

The quickest and easiest way to serve the site locally is to use https://github.com/BretFisher/jekyll-serve

```bash
cd docs

docker run --rm  -p 4000:4000 -v $(pwd):/site bretfisher/jekyll-serve
```

When plugin installation is complete, open a browser to http://0.0.0.0:4000/ble_monitor/

## Notes about theme being used.

* Values are displayed through the device HTML template, `docs/_includes/device.html`
* Addtional notes can be added below the block of properties.
* Additional properties can be added as needed.  Simply add to the property to each device markdown file and display it accordingly in the template.
* `physical_description`, `broadcast_rate`, `active_scan`, `encryption_key`, `custom_firmware` are hidden when the value is false.

A few modifications were make to the standard navigation found in the [Just-the-docs theme](https://github.com/pmarsceill/just-the-docs).  This is to show the child pages under "Supported Devices" at all times.
* Table of content generation uses a modified version of [allejo/jekyll-toc v1.1.0](https://github.com/allejo/jekyll-toc).
