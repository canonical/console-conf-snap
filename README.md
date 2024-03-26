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
$ snap connections console-conf
Interface              Plug                                Slot                           Notes
custom-device          console-conf:terminal-control       console-conf:terminal-devices  -
hardware-observe       console-conf:hardware-observe       :hardware-observe              -
network                console-conf:network                :network                       -
network-control        console-conf:network-control        :network-control               -
network-observe        console-conf:network-observe        :network-observe               -
network-setup-control  console-conf:network-setup-control  :network-setup-control         -
snapd-control          console-conf:snapd-control          :snapd-control                 -
system-files           console-conf:run-console-conf       :system-files                  -
system-files           console-conf:var-log-console-conf   :system-files                  -
```

For a snap installed from the snap store, the connections should be established
automatically, however when working with a development version built with
snapcraft (or some other way), you need to `snap connect` these manually.
