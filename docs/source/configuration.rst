.. _configuration:

Configuration
-------------

The configuration file specifies how the datasets should be downloaded, or
if the datasets do no have to be downloaded (e.g. on Google Cloud).

The configuration file should be at ``$HOME/.deel/config.yml``:

* On Windows system it is ``C:\Users\$USERNAME\.deel\config.yml`` unless you
  have set the `HOME` environment variable.
* The ``DEEL_CONFIGURATION_FILE`` environment variable can be used to specify the
  location of the configuration file if you do not want to use the default one.

The configuration file is a **YAML** file.

Two root nodes are mandatory in configuration file:

* ``providers:`` (value = list of providers)

* ``path``: local destination directory path (by default = ${HOME}/.deel/datasets)

    .. code-block:: bash

      providers:
          ├── provider1
          ├── provider1
          ├── provider1
          ├── .
          ├── .
          ├── .
          └── providerN
      path: local destination path

``providers`` is the root node of the provider configurations list.
Each child node of `providers` node define a provider configuration.
The name of child node is the name of the provider.
It may be used in command line to specify the provider (e.g., option ``-p`` for ``download``).

Currently the following types of provider are implemented: ``webdav``, ``ftp``, ``http``, ``local`` and ``gcloud``.

* The ``webdav`` provider will fetch datasets from a WebDAV server and needs at least the ``url``
  configuration parameter.
  The WebDAV provider supports basic authentication (see example below).
  If the datasets are not at the root of the WebDAV server, the `folder` configuration can be used to
  specify the remote path (see example below).

* The ``ftp`` provider is similar to the ``webdav`` provider except that it will fetch datasets
  from a FTP server instead of a WebDAV one and needs at least the ``url`` configuration parameter.

* The ``local`` provider does not require any extra configuration and will simply fetch data from
  the specified ``path``. The ``copy``configuation (true or false) allows to specify if dataset
  must be copied from ``path`` to destination ``path`` or not. ``copy`` is false by default.

* The ``gcloud`` provider is similar to the ``local`` provider, except that it will try to
  locate the dataset storage location automatically based on a mounted drive.
  The ``disk`` configuration parameter is mandatory and specify the name of the GCloud drive.

``path`` parameter indicates where the datasets should be stored locally when using remote providers such as `webdav`, `http` or `ftp` provider.

Configuration Example
.....................

.. code-block:: YAML

   providers:

  # A GCloud provider with a shared GCloud drive named "my-disk-name".
  gcloud:
    type: gcloud
    disk: my-disk-name

  # A local storage at "/data/dataset".
  local:
    type: local
    path: /data/dataset/
    copy: true

  # An FTP provider.
  ftp:
    type: ftp
    # The "url" parameter contains the full path (server + folder):
    url: ftp://<server_name>/<dataset path on ftp server>
    # or folder to set the the path to dataset remote directory
    # folder: <dataset path on ftp server>
    # The "auth" is optional if the FTP server is public:
    auth:
      method: "simple"
      username: "${username}"
      password: "${password}"

  # A public WebDAV server.
  webdav_public:
    type: webdav
    url: https://my-public-webdav.com

  # A private WebDAV server where the datasets are not at the root.
  # Note: This example can be used with Cloud storage such as Nextcloud with
  # a shared "datasets" drive.
  webdav_private:
    type: webdav
    url: https://my-cloud-provider.com/remote.php/webdav
    folder: datasets
    auth:
        method: "simple"
        username: "${username}"
        password: "${password}"

  # The local path where datasets are stored when they are from a remote provider:
  # by default ${HOME}/.deel/datasets
  path: ${HOME}/.deel/datasets
