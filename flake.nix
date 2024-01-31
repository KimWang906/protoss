{
  description = "PWNABLE Shell env";

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
      pkgs.mkShell {
          buildInputs = with pkgs; [
            pwndbg
            tmux
            pwntools
            checksec
            ropgadget
            one_gadget
          ];

          shellHook = ''
            cp config/.tmux.conf $HOME
            tmux
            alias gdb="pwndbg"
          '';
        };
  };
}
