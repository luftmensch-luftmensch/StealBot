with import <nixpkgs> { };

let

  postgresConf =
    writeText "postgresql.conf"
      ''
        log_min_messages = warning
        log_min_error_statement = error
        log_min_duration_statement = 100  # ms
        log_connections = on
        log_disconnections = on
        log_duration = on
        log_timezone = 'UTC'
        log_statement = 'all'
        log_directory = 'logs'
        log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
        logging_collector = on
        log_min_error_statement = error
      '';

  pg_hostname = "localhost";
  pg_port     =  "5432";
  pg_user     =  "username";
  pg_db       =  "postgres";


in pkgs.mkShell rec {
  name = "ephimeral-postgres-shell";

  PGDATA = "${toString ./.}/.pg/";

  buildInputs = [ postgresql_14 less ];

  shellHook = ''
    printf "\e[36m%b\e[0m\n" "Using ${postgresql_14.name}"
    export PGHOST="${pg_hostname}"
    export PGPORT="${pg_port}"
    export PGUSER="${pg_user}"
    export PGDATABASE="${pg_db}"

    printf "\e[36m%b\e[0m\n" "$PGHOST, $PGPORT, $PGUSER, $PGDATABASE"


    [ ! -d $PGDATA ] && PGHOST="$PGDATA" pg_ctl initdb -o "-U $PGUSER" && cat "$postgresConf" >> $PGDATA/postgresql.conf

    pg_ctl -o "-p $PGPORT -k $PGDATA" start && {
      trap 'pg_ctl stop' EXIT
    }

    '';
}
