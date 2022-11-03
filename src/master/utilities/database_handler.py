"""Database handler for bot-master source code."""
import psycopg2
from psycopg2 import Error  # Eccezioni custom della libreria ad hoc per postgresql

# Librerie personali
from . import bot_master_utility as bot_master_utils


class DatabaseHandler:
    """Classe Handler per la gestione del database."""

    """
    Definiamo una serie di variabili "private".
    Visto che di default il linguaggio non offre nessuna keyword `private`
    aggiungendo __ all'inizio di una variabile (naming convention) la definiamo
    come internal (Non è quindi accessibile)
    """
    __database_host = "192.168.1.36"
    __database_port = "5432"
    __database_name = "botnet"
    __database_username = "username"
    __database_password = "password"

    __connection_alive = True

    # TODO: Controllare che la dimensione fissata dei campi delle tabelle sono sufficienti (Sono le 3 e non ho la minima voglia di controllare @francywolf)
    # TODO: Controllare che sia necessario definire i campi delle tabelle NOT NULL (Sono le 3 e non ho la minima voglia di controllare @francywolf). Io rn: https://www.youtube.com/watch?v=5IZ_POEeiAA
    """
    La PRIMARY KEY è definita come SERIAL in modo da poter essere automaticamente autoincrementabile (Nella query non siamo obbligati a passare il campo ID)
    """
    __botclient_table_definition = "CREATE TABLE IF NOT EXISTS  botclient (ID SERIAL PRIMARY KEY NOT NULL, HOSTNAME VARCHAR(50) NOT NULL);"

    __botclient_cpu_informations = """CREATE TABLE IF NOT EXISTS cpu_informations
                                      (CPU_ID INT PRIMARY KEY NOT NULL, BOTCLIENT_CPU_ID INT NOT NULL, BRAND VARCHAR(100), CPU_COUNT VARCHAR(100),
                                       CPU_COUNT_LOGICAL VARCHAR(100), MIN_FREQ VARCHAR(20), MAX_FREQ VARCHAR(20),
                                       CONSTRAINT botnet_cpu_fk FOREIGN KEY(BOTCLIENT_CPU_ID) REFERENCES botclient(ID));"""

    __botclient_ram_informations = '''CREATE TABLE IF NOT EXISTS ram_informations
                                      (RAM_ID INT PRIMARY KEY NOT NULL, BOTCLIENT_RAM_ID INT NOT NULL, USED_MEM VARCHAR(40), TOTAL_MEM VARCHAR(40),
                                       CONSTRAINT botnet_ram_fk FOREIGN KEY(BOTCLIENT_RAM_ID) REFERENCES botclient(ID));'''

    __botclient_os_informations = '''CREATE TABLE IF NOT EXISTS os_informations
                                      (OS_ID INT PRIMARY KEY NOT NULL, BOTCLIENT_OS_ID INT NOT NULL, TYPE VARCHAR(50) NOT NULL,
                                       CONSTRAINT botnet_os_fk FOREIGN KEY(BOTCLIENT_OS_ID) REFERENCES botclient(ID));'''

    __botclient_users_informations = '''CREATE TABLE IF NOT EXISTS user_informations
                                        (USER_ID INT PRIMARY KEY NOT NULL, BOTCLIENT_USER_ID INT NOT NULL, NAME VARCHAR(100) NOT NULL,
                                         CONSTRAINT botnet_user_fk FOREIGN KEY(BOTCLIENT_USER_ID) REFERENCES botclient(ID));'''

    __botclient_disk_io_counter_informations = '''CREATE TABLE IF NOT EXISTS disk_io_counters_informations
                                                  (DISK_IO_ID INT PRIMARY KEY NOT NULL, BOTCLIENT_DISK_IO_ID INT NOT NULL,
                                                   READ_BYTES VARCHAR(50) NOT NULL, WRITTEN_BYTES VARCHAR(50) NOT NULL,
                                                   CONSTRAINT botnet_disk_io_fk FOREIGN KEY(BOTCLIENT_DISK_IO_ID) REFERENCES botclient(ID));'''

    __botclient_disk_partitions_informations = '''CREATE TABLE IF NOT EXISTS disk_partitions_informations
                                                  (DISK_PARTITION_ID INT PRIMARY KEY NOT NULL, BOTCLIENT_DISK_PARTITION_ID INT NOT NULL,
                                                   DEVICE VARCHAR(70) NOT NULL, MOUNTPOINT VARCHAR(50) NOT NULL, FSTYPE VARCHAR(50) NOT NULL,
                                                   CONSTRAINT botnet_disk_partition_fk FOREIGN KEY(BOTCLIENT_DISK_PARTITION_ID) REFERENCES botclient(ID));'''

    __botclient_network_informations = '''CREATE TABLE IF NOT EXISTS network_informations
                                          (NETWORK_ID INT PRIMARY KEY NOT NULL, BOTCLIENT_NETWORK_ID INT NOT NULL,
                                           INTERFACE VARCHAR(30), IP VARCHAR(40), NETMASK VARCHAR(40), BROADCAST_IP VARCHAR(50),
                                           CONSTRAINT botnet_network_fk FOREIGN KEY(BOTCLIENT_NETWORK_ID) REFERENCES botclient(ID));'''

    # Utilizziamo un dictionary per avere una informazione più chiara dell'operazione che il server sta eseguendo (creazione della tabella X corrispondente a una key all'interno di __invoke_all)
    __invoke_all = {"botclient": __botclient_table_definition,
                    "cpu_informations": __botclient_cpu_informations,
                    "disk_io_counters_informations": __botclient_disk_io_counter_informations,
                    "disk_partitions_informations": __botclient_disk_partitions_informations,
                    "network_informations": __botclient_network_informations,
                    "os_informations": __botclient_os_informations,
                    "ram_informations": __botclient_ram_informations,
                    "user_informations": __botclient_users_informations}

    def database_init(db_host: str, db_port: int, db_name: str, db_username: str, db_password: str) -> bool:
        """Funzione di setup del database."""
        bot_master_utils.info("Inizializzazione database", 2)
        try:
            connection = psycopg2.connect(host=db_host, port=db_port, database=db_name,
                                          user=db_username, password=db_password)

            # Creazione di un cursore per effettuare operazioni
            cursor = connection.cursor()

            # Per brevità all'avvio le eseguiamo tutte con un ciclo (evitiamo di avere codice ripetitivo sfruttando un dictionary che contenga tutte le query)
            for key in DatabaseHandler.__invoke_all:
                cursor.execute(DatabaseHandler.__invoke_all[key])
                bot_master_utils.info(f"Creazione della tabella {key} avvenuta con successo", 1)
            connection.commit()

            if (connection):
                cursor.close()
                connection.close()
                bot_master_utils.info("Chiusura della connessione al database PostgreSQL effettuata con successo!", 2)

        except (Exception, Error) as error:
            bot_master_utils.info(f"Errore durante la connessione al database: {error}", 3)
            return False
        return True

        # L'obiettivo è quello di fare operazioni con il dbms che siano "atomiche" e "isolate" -> Ergo una volta finita l'operazione chiudiamo la connessione
        # finally:

    def database_insert(query: str) -> None:
        """Funzione di inserimento di un record nel database."""
        bot_master_utils.info("Inserimento dati nel database in corso", 2)
        try:
            with psycopg2.connect(host=DatabaseHandler.__database_host, port=DatabaseHandler.__database_port,
                                  database=DatabaseHandler.__database_name, user=DatabaseHandler.__database_username,
                                  password=DatabaseHandler.__database_password) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    connection.commit()
        except Error as e:
            bot_master_utils.info(f"Errore nell'esecuzione dello statement: {e}", 2)
        finally:
            if (connection):
                cursor.close()
                connection.close()
                bot_master_utils.info("Chiusura della connessione al database PostgreSQL effettuata con successo!", 2)

    def database_insert_new_client(hostname: str) -> None:
        """Funzione di inserimento di un nuovo client all'interno del dbms."""
        bot_master_utils.info("Inserimento di un nuovo client nel database in corso", 2)
        try:
            with psycopg2.connect(host=DatabaseHandler.__database_host, port=DatabaseHandler.__database_port,
                                  database=DatabaseHandler.__database_name, user=DatabaseHandler.__database_username,
                                  password=DatabaseHandler.__database_password) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(f"INSERT INTO botclient(hostname) values('{hostname}')")
                    connection.commit()

                if (connection):
                    cursor.close()
                    connection.close()
                    bot_master_utils.info("Chiusura della connessione al database PostgreSQL effettuata con successo!", 2)

        except Error as e:
            bot_master_utils.info(f"Errore nell'esecuzione dello statement: {e}", 2)

    def database_select(query: str):
        """Funzione di retrieval di tutti i record presenti nel database."""
        bot_master_utils.info("Recupero dati dal database in corso", 2)
        try:
            with psycopg2.connect(host=DatabaseHandler.__database_host, port=DatabaseHandler.__database_port,
                                  database=DatabaseHandler.__database_name, user=DatabaseHandler.__database_username,
                                  password=DatabaseHandler.__database_password) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    return cursor.fetchall()

                if (connection):
                    cursor.close()
                    connection.close()
                    bot_master_utils.info("Chiusura della connessione al database PostgreSQL effettuata con successo!", 2)
        except Error as e:
            bot_master_utils.info(f"Errore nell'esecuzione dello statement: {e}", 2)

    def database_select_all():
        """Funzione di retrieval di tutti i record nel database."""

    def database_remove_record(query: str):
        """Funzione di rimozione di un record presente nel database."""

    def database_remove_all_record(query: str):
        """Funzione di rimozione di tutti i record presenti nel database."""

    def database_drop_all() -> None:
        """Funzione di reset del database."""
        bot_master_utils.info("Inizializzazione statement per l'eliminazione di tutte le tabelle presenti sul database", 1)
        try:
            with psycopg2.connect(host=DatabaseHandler.__database_host, port=DatabaseHandler.__database_port,
                                  database=DatabaseHandler.__database_name, user=DatabaseHandler.__database_username,
                                  password=DatabaseHandler.__database_password) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';")
                    tables = [i[0] for i in cursor.fetchall()]  # Convertiamo una tupla in un array (Prendiamo il primo campo)
                    for table in tables:
                        bot_master_utils.info(f"Eliminazione tabella {table} database", 1)
                        cursor.execute(f"DROP TABLE public.{table} CASCADE;")
                connection.commit()

                if (connection):
                    cursor.close()
                    connection.close()
                    bot_master_utils.info("Chiusura della connessione al database PostgreSQL effettuata con successo!", 2)

        except Error as e:
            bot_master_utils.info(f"Errore nell'esecuzione dello statement: {e}", 2)

    def handle_request():
        """Funzione per la gestione delle request (interrogazioni) dell'utente al database."""
        # print()
        if DatabaseHandler.__connection_alive is False:
            bot_master_utils.info(f"Attenzione! Non è stato possibile collegarsi al database {DatabaseHandler.__database_name} sull'host {DatabaseHandler.__database_host}:{DatabaseHandler.__database_port}", 3)
        else:
            print("All Done")

    @classmethod
    def __init__(self):
        """Invocazione automatica della funzione di init."""
        self.__connection_alive = self.database_init(self.__database_host, self.__database_port, self.__database_name,
                                                     self.__database_username, self.__database_password)
