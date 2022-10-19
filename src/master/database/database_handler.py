"""Database handler for bot-master source code."""
import psycopg2
from psycopg2 import Error  # Eccezioni custom della libreria ad hoc per postgresql


class DatabaseHandler:
    """Classe Handler per la gestione del database."""

    """
    Definiamo una serie di variabili "private".
    Visto che di default il linguaggio non offre nessuna keyword `private`
    aggiungendo __ all'inizio di una variabile (naming convention) la definiamo
    come internal (Non è quindi accessibile)
    """

    __database_host = "192.168.1.36"  # TODO: Cambiare in produzione
    __database_port = "5432"  # TODO: Cambiare in produzione
    __database_name = "botnet"
    __database_table_name = "botnet"
    __database_username = "username"  # TODO: Cambiare in produzione
    __database_password = "password"  # TODO: Cambiare in produzione

    # TODO: Aggiungere in seguito i campi necessari al salvataggio dei dati
    __create_table_query = ''' CREATE TABLE IF NOT EXISTS botnet
        (ID INT PRIMARY KEY NOT NULL,
        HOSTNAME VARCHAR(50) NOT NULL,
        CPU VARCHAR(50) NOT NULL);
        '''

    def database_init(db_host: str, db_port: int, db_name: str, db_username: str, db_password: str):
        """Funzione di setup del database."""
        print("[+] Inizializzazione database\n")
        try:
            connection = psycopg2.connect(host=db_host, port=db_port, database=db_name,
                                          user=db_username, password=db_password)

            # Creazione di un cursore per effettuare operazioni
            cursor = connection.cursor()

            # Creazione della tabella necessaria ai record da salvare con la botnet
            cursor.execute(DatabaseHandler.__create_table_query)
            print("[+] Creazione della tabella avvenuta con successo\n")

        except (Exception, Error) as error:
            print("[!] Errore durante la connessione al database: ", error)

        finally:
            if (connection):
                cursor.close()
                connection.close()
                print("[+] Chiusura della connessione al database PostgreSQL effettuata con successo!\n")

    def database_insert(query: str):
        """Funzione di inserimento di un record nel database."""

    def database_select(query: str):
        """Funzione di retrieval di tutti i record presenti nel database."""

    def database_select_all():
        """Funzione di retrieval di tutti i record nel database."""

    def database_remove_record(query: str):
        """Funzione di rimozione di un record presente nel database."""

    def database_remove_all_record(query: str):
        """Funzione di rimozione di tutti i record presenti nel database."""

    @classmethod
    def __init__(self):
        """Invocazione automatica della funzione di init."""
        self.database_init(self.__database_host, self.__database_port, self.__database_name,
                           self.__database_username, self.__database_password)
