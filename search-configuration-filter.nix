{ config, pkgs, ... }:

{
  environment.systemPackages = with pkgs; [
    (writeScriptBin "cs" ''
      #!${pkgs.bash}/bin/bash
      ${pkgs.python3}/bin/python3 /path/to/nixos-configuration-filter/search.py "$@"  #UPDATE TO YOUR LOCAL REPO LOCATION PATH
    '')
  ];
}
