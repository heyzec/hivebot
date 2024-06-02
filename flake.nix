{
  description = "Template for a direnv shell, with Python + Poetry";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    poetry2nix.url = "github:nix-community/poetry2nix";
  };

  outputs = { self, nixpkgs, poetry2nix }:
  let
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};
    inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication defaultPoetryOverrides;

    pypkgs-build-requirements = {
      importhook = [ "setuptools" ];
    };
    p2n-overrides = defaultPoetryOverrides.extend (final: prev:
      builtins.mapAttrs (package: build-requirements:
        (builtins.getAttr package prev).overridePythonAttrs (old: {
          buildInputs = (old.buildInputs or [ ]) ++ (builtins.map (pkg: if builtins.isString pkg then builtins.getAttr pkg prev else pkg) build-requirements);
        })
      ) pypkgs-build-requirements
    );


    myPythonApp = mkPoetryApplication {
      preferWheels = true;
      projectDir = ./.;
      overrides = p2n-overrides;
    };
  in
  {
    devShells.${system}.default = pkgs.mkShell {
      buildInputs = with pkgs; [
        poetry
        myPythonApp
      ];
    };
  };
}

