# Sandbox-Graph-Comparator
A comparator for Apple Sandbox profiles

Compares an SBPL Sandbox Profile against its decompiled form, provided by
[SandBlaster](https://github.com/malus-security/sandblaster). The profiles are
compiled as graphs and a `diff`-like output with missing rules and filters is
printed. The graph representation of the SBPL profile is obtained using
[SandScout](https://github.com/malus-security/sandscout).
