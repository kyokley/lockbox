{ pkgs, lib, config, inputs, ... }:

{
  # https://devenv.sh/basics/
  env = {
    GREET = "lockbox";
    USE_HOST_NET = 1;
    PYTHONPATH = ".";
  };

  # https://devenv.sh/packages/
  packages = [];

  # https://devenv.sh/languages/
  languages.python = {
    enable = true;
    version = "3.12";
    venv.enable = true;
    uv.enable = true;
  };

  # https://devenv.sh/processes/
  # processes.cargo-watch.exec = "cargo-watch";

  # https://devenv.sh/services/
  # services.postgres.enable = true;

  # https://devenv.sh/scripts/
  scripts = {
    hello.exec = ''
      echo Welcome to $GREET
    '';
    build.exec = ''
      docker build --target=final -t kyokley/lockbox $(test $USE_HOST_NET -eq 1 && echo "--network=host") .
    '';
    build-dev.exec = ''
      docker build --target=dev -t kyokley/lockbox $(test $USE_HOST_NET -eq 1 && echo "--network=host") .
    '';
    tests.exec = ''
      build-dev
      docker run --rm -t --entrypoint uv -v $(pwd):/code --workdir /code kyokley/lockbox run pytest
    '';
    lockbox.exec = ''
      uv run python lockbox "$@"
    '';
    publish.exec = "build && docker push kyokley/lockbox";
    shell.exec = ''
      docker run --rm -it --entrypoint bash -v $(pwd):/code kyokley/lockbox
    '';
  };

  enterShell = ''
    hello
  '';

  # https://devenv.sh/tasks/
  # tasks = {
  #   "myproj:setup".exec = "mytool build";
  #   "devenv:enterShell".after = [ "myproj:setup" ];
  # };

  # https://devenv.sh/tests/
  enterTest = ''
    echo "Running tests"
    tests
  '';

  # https://devenv.sh/git-hooks/
  git-hooks.hooks = {
    ruff.enable = true;
    ruff-format.enable = true;
  };

  # See full reference at https://devenv.sh/reference/options/
}
