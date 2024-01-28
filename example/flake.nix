{
  description = "Protobuf build env";

  input = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  }

  outputs = { self, nixpkgs }: 
  let 
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};
  {
    devShells.${system}.default = 
      pkgs.mkShell
        {
          buildInputs = [
            pkgs.protobuf_25
            pkgs.cmake
            pkgs.zlib
          ];
        }
  };
}
