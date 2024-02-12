{
  description = "Protobuf build env";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }: 
  let 
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};
  in
  {
    devShells.${system}.default = 
      pkgs.mkShell
        {
          buildInputs = with pkgs; [
            protobuf_25
            cmake
            zlib
            abseil-cpp_202308
            pkgs.autoPatchelfHook
          ];



          shellHook = ''
            echo ${pkgs.abseil-cpp_202308}
            cmake -Bout
            cmake --build out
            patchelf \
              --add-needed \
              ${pkgs.abseil-cpp_202308}/lib/libabsl_log_internal_check_op.so.2308.0.0 \
              out/build/main
            patchelf \
              --add-needed \
              ${pkgs.abseil-cpp_202308}/lib/libabsl_log_internal_message.so.2308.0.0 \
              out/build/main
          '';
        };
  };
}
