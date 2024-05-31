{
  description = "Template for a direnv shell, with Python";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
  let
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};

    importhook = ps: let
      pname = "importhook";
      version = "1.0.9";
    in ps.buildPythonPackage {
      inherit pname version;

      src = pkgs.fetchFromGitHub {
        owner = "rkargon";
        repo = "importhook";
        rev = "5c8df7a9c5060eb66f32f2c44bb60ba0aaf65d2f";
        sha256 = "sha256-WyScHcAOEO0ASEF8IWHoPSPZGnCPq8b+eGSNtV/WNSY=";
      };
      doCheck = false;
    };

  in
  {
    devShells.${system}.default = pkgs.mkShell {
      buildInputs = with pkgs; [
        (let
          python-packages = ps: with ps; [
            python-dotenv

            (importhook ps)

            python-telegram-bot
          ];
        in python3.withPackages python-packages)
      ];
    };
  };
}

