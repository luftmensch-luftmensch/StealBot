# Taken from https://nixos.org/manual/nixpkgs/stable/#how-to-consume-python-modules-using-pip-in-a-virtual-environment-like-i-am-used-to-on-other-operating-systems
with import <nixpkgs> { };

let
  pythonPackages = with pkgs.python310Packages; [

    # A Python interpreter including the 'venv' module is required to bootstrap
    # the environment.
    #python310

    # This execute some shell code to initialize a venv in $venvDir before
    # dropping into the shell
    venvShellHook

    # Those are dependencies that we would like to use from nixpkgs, which will
    # add them to PYTHONPATH and thus make them accessible from within the venv.
    requests
    
  ];
in pkgs.mkShell rec {
  name = "impurePythonEnv";
  venvDir = "./.venv";
  buildInputs = [
    python310
    pythonPackages

    # In this particular example, in order to compile any binary extensions they may
    # require, the Python modules listed in the hypothetical requirements.txt need
    # the following packages to be installed locally:
    taglib
    #openssl
    git
    libxml2
    libxslt
    libzip
    zlib
  ];

    

  # Run this command, only after creating the virtual environment
  postVenvCreation = ''
    unset SOURCE_DATE_EPOCH
    pip install -r requirements.txt
  '';

  # Now we can execute any commands within the virtual environment.
  # This is optional and can be left out to run pip manually.
  postShellHook = ''
    # allow pip to install wheels
    unset SOURCE_DATE_EPOCH
    # Don't create __pycache_ directory
    # export PYTHONDONTWRITEBYTECODE=1

    master1(){
         export PS1="\[\e[1;32m\][\w] master [PORT: 9000] > \[\e[0m\]"
         cd ~/UNI/StealBot/src/master
    }

    master2(){
         export PS1="\[\e[1;32m\][\w] master [PORT: 9001] > \[\e[0m\]"
         cd ~/UNI/StealBot/src/master
    }

    slave(){
         export PS1="\[\e[1;32m\][\w] slave > \[\e[0m\]"
         cd ~/UNI/StealBot/src/slave
    }

    dispatcher(){
         export PS1="\[\e[1;32m\][\w] dispatcher [PORT: 9090] > \[\e[0m\]"
         cd ~/UNI/StealBot/src/master

    }

    run-dispatcher(){
         python main.py --port=9090 --supervisor=dispatcher

    }
  '';

}
