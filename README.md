# Sandbox-Graph-Comparator
A comparator for Apple Sandbox profiles

Compares an *iOS* SBPL Sandbox Profile against its decompiled form, provided by
[SandBlaster](https://github.com/malus-security/sandblaster). The profiles are
compiled as graphs and a `diff`-like output with missing rules and filters is
printed. The graph representation of the SBPL profile is obtained using
[SandScout](https://github.com/malus-security/sandscout).


## Running the script
First, you'll need to initialise the two submodules:
```bash
$ cd sandblaster
$ git submodule init
$ cd ../sandscout
$ git submodule init
```

Then you can run `compare_profiles.py` by providing it with 2 input files: one
original *SBPL* and another bianry profile. One example is:
```bash
python3 compare_profiles.py -o original.sbpl -d profile.bin -r 8.4 --ops sb_ops
```

Alternatively, if the binary profile has been previously decompiled to *SBPL*,
the decompilation step can be skipped (and the running time reduced) by merely
parsing the resulting *SBPL* file using
[SandScout](https://github.com/malus-security/sandscout) once more. In order to
do this, pass the `--sbpl` parameter to the script, as shown in the example
below:
```bash
python3 compare_profiles.py -o original.sbpl -d decompiled.sbpl --sbpl
```

### Comparing all profiles in an iOS version
In order to validate all profiles in an *iOS* release, you first need the
following hierarchy:
```
samples
├── <release_less_than_ios9>
│   ├── reversed_profiles/
|       ├── a.sb
|       ├── b.sb
|       ...
|       └── x.sb
│   ├── binary_profiles
|       ├── a.bin
|       ├── b.bin
|       ...
|       └── x.bin
|   └── sb_ops
├── <release_more_than_ios9>
│   ├── reversed_profiles
|       ├── a.sb
|       ├── b.sb
|       ...
|       └── x.sb
│   ├── sandbox_bundle
|   └── sb_ops
├── ...

```
Then, call the script `compare_all_profiles.sh` and provide it with the name of
the release and *iOS* version like so:
```bash
./compare_all_profiles.sh iPhone5,1_9.3_13E237 9.3
```

The script will create (if it doesn't already exist) a `diffs/<release>` folder
inside the `samples` directory, where the would-be differences between the
compiled and decompiled profiles would be found:

```
samples/
├── diffs
│   └── <release>
│       ├── a.diff
│       ├── b.diff
│       ├── ...
│       └── x.diff
```
