{
  description = "Template for a direnv shell, with Python + Poetry";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    poetry2nix.url = "github:nix-community/poetry2nix";
  };

  outputs = { self, nixpkgs, poetry2nix }:
  let
    systems = [ "x86_64-linux" "aarch64-linux" ];

    pkgsForSystem = system: nixpkgs.legacyPackages.${system};

    myPythonAppForSystem = system: let
      pkgs = pkgsForSystem system;

      inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryEnv defaultPoetryOverrides;

      mkOverrides = req: defaultPoetryOverrides.extend (final: prev:
        builtins.mapAttrs (package: build-requirements:
          (builtins.getAttr package prev).overridePythonAttrs (old: {
            buildInputs = (old.buildInputs or [ ]) ++ (builtins.map (pkg: if builtins.isString pkg then builtins.getAttr pkg prev else pkg) build-requirements);
          })
        ) req
      );

    in
      mkPoetryEnv {
        preferWheels = true;
        projectDir = ./.;
        overrides = mkOverrides {
          importhook = [ "setuptools" ];
        };
      };
  in {
    devShells = nixpkgs.lib.genAttrs systems (system: let
      pkgs = pkgsForSystem system;
      myPythonApp = myPythonAppForSystem system;
    in {
      default = pkgs.mkShell {
        buildInputs = with pkgs; [
          poetry
          myPythonApp
        ];
      };
    });

    packages = nixpkgs.lib.genAttrs systems (system: {
      default = (pkgsForSystem system).writeShellScriptBin "entrypoint" ''
        export PYTHONPATH="${myPythonAppForSystem system}/lib/python3.11/site-packages";
        python main.py
      '';
    });
  };
}
