# console-conf packaged as a snap

> console-conf provides first boot experience for Ubuntu Core

The repository contains the source to package console-conf and ubiquity
as a strictly confined snap.


## Building

Use `snapcraft` to build the console-conf snap.

## Using

The following snap interface connections must be established before console-conf
can be used:

```
$ snap connections
Interface              Plug                                       Slot                           Notes
custom-device          console-conf:terminal-control              console-conf:terminal-devices  manual
hardware-observe       console-conf:hardware-observe              :hardware-observe              manual
network                console-conf:network                       :network                       -
network-control        console-conf:network-control               :network-control               manual
network-observe        console-conf:network-observe               :network-observe               manual
network-setup-control  console-conf:network-setup-control         :network-setup-control         manual
snapd-control          console-conf:snapd-control                 :snapd-control                 manual
system-files           console-conf:console-conf-runtime-support  :system-files                  manual
```

Once the snap is published to the store and permissions are granted, the
connections will be established automatically.
