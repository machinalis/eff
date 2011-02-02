=======
Install
=======

- Add data base credentials here:

  * If you are going to use a DotProject source:
    sitio/scripts/dotproject.py
    class Machinalis(DotProject):
        ...
        DB = ''
        DB_USER = ''
        PASSWD = ''
        ...

  * sitio/settings.py
   DATABASE_NAME = ''           # Or path to database file if using sqlite3.
   DATABASE_USER = ''           # Not used with sqlite3.
   DATABASE_PASSWORD = ''          # Not used with sqlite3.

   SECRET_KEY = ''

  * For Jira source of logs you should add it in the source when you create it in the admin


========================
Migración de datos a Eff
========================

Requisitos para crear un script de migración de una fuente X a Eff
==================================================================

- Crear un script en el directorio sitio/scripts (por ejemplo: fuentex.py), este debe incluir 
  una función global llamada fetch_all con las siguientes características:
  
  :Parámetros: 
  
  1. source: de tipo sitio.eff._models.external_source.ExternalSource (un source existente en la base de datos)
  2. client: de tipo sitio.eff._models.client.Client (Un cliente existente en la base de datos)
  3. author: de tipo str que será el identificador de usuario para el dump de los logs importados al sistema.
  4. from_date: de tipo datetime.datetime que corresponde a la fecha de inicio de los logs importados al sistema.
  5. to_date: de tipo datetime.datetime que corresponde a la fecha de fin de los logs importados al sistema.
  6. _file: de tipo file object, donde se guardaran los logs recuperados de la fuente externa antes de ser importados.

  :Cuerpo de la función (IMPORTANTE): Debe incluirse funcionalidad particular para recuperar los logs de la fuente X y luego utilizar la clase sitio.eff.utils.EffCsvWriter sobre _file para generar el csv con formato de Eff, ya que el mismo debe tener la estructura csv requerida para importar a Eff.

- Incluir la asociación con la fuente externa en sitio/scripts/config.py en el diccionario EXT_SRC_ASSOC.
  Por ejemplo si nuestra instancia de ExternalSource tiene nombre "FuenteX" y nuestro script se llama "fuentex.py" agregaríamos "'FuenteX' : 'fuentex'" al diccionario antes mencionado.


Como migrar de datos a Eff desde una fuente externa
===================================================

Previamente creado el script de migración como se explicó en la sección anterior, para realizar una migración desde una fuente externa X (supongamos una instancia de ExternalSource con atributo name "FuenteX", como antes) entre dos fechas dadas (por ejemplo entre el 1ro de julio de 2010 y el 31 de julio de 2010), debemos ejecutar sitio/scripts/fetch_all.py de la siguiente forma:

$ python fetch_all.py FuenteX 20100701 20100731

