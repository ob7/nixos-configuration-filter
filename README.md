# nixos-configuration-filter

Filters the output of "man configuration.nix" to whatever prefix is provided on the prompt

This script filters the content of the `configuration.nix` man page to display only the sections matching a specified prefix. It’s designed to help you quickly find specific configuration options in the NixOS documentation without needing to scroll through unrelated sections.

## Usage

To filter by a specific prefix, pass the desired prefix as an argument to the script. For example:

```bash
python search.py virtualisation.virtualbox
```

This command will generate an output containing only the configuration options under `virtualisation.virtualbox` in the `configuration.nix` man page.

### Description-Only Output

To limit the output to descriptions only, omitting data types and other fields, use the `-d` option:

```bash
python search.py -d virtualisation.virtualbox.host
```

This command will return only the descriptions for `virtualisation.virtualbox.host` entries, providing a more compact view of available configuration options.

## Why Use This?

This tool is ideal when you want to quickly view specific configuration options in the `configuration.nix` man page, especially when you’re looking for descriptions only. It reduces clutter and allows for a more streamlined search experience.

---

This tool is particularly useful for NixOS users who need quick, targeted information from the man page without unnecessary details.

### Global Usage

The provided search-configuration-filter.nix can be imported into your configuration.nix and used to map the script to a unique command name for easy usage from any terminal.  Update the path to your local copy.  The example maps the command to "cs", allowing you to run the script from anywhere, such as 
```bash
cs virtualisation.virtualbox.host
```
or
```bash
cs -d virtualisation.virtualbox
```
