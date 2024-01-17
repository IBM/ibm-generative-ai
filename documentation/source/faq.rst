.. _faq:

FAQ
===

.. contents::
   :local:
   :class: this-will-duplicate-information-and-it-is-still-useful-here


SDK ignores SIGINT/SIGTERM signals
----------------------------------

We use `asyncio` under the hood, running in its own thread to achieve maximal performance. This means signals from the main
thread are not propagated; thus, SDK does not know you want to exit. To make SDK reacts to such signal, you need to
call our prepared function.

Example can be found :ref:`here <examples.extra.shutdown_handling>`.


Which endpoints version SDK uses?
---------------------------------

Use the following options to determine which version of a given endpoint SDK uses.

1. From the :doc:`Changelog <changelog>` ("API Endpoint Versions" section) under concrete release.

2. Find it programmatically by retrieving the concrete method's metadata (see :ref:`example <examples.extra.service_metadata>`).


When I run multiple text generations simultaneously one is hanging, how to fix that?
------------------------------------------------------------------------------------

When you run a text generation task, the SDK first retrieves your maximal concurrency limit (this limit can vary from
user to user, but generally, there is a default) and use it as the upper bound.
This implies that the different processes may get stack or even error.
To prevent such a situation, you can set your maximal limit for each execution via the `execution_options` parameter.

Such an example with multiple limits and processes can be found :ref:`here <examples.extra.parallel_processing>`.


.. admonition:: Concurrency limiting without threading/multiprocessing
   :class: note

   For a single instance of the SDK, concurrency handling is done automatically, but you can still limit the number of requests.


.. admonition:: How to find out your current limits?
   :class: note

   To find your limit, use the following methods ``client.text.generation.limit.retrieve`` (text) / ``client.text.embedding.limit.retrieve`` (embeddings).
   If your service is not mentioned, try to find the `limit` attribute.


.. admonition:: How to increase your limit?
   :class: note

   Contact administrator or your manager.


SSL_CERTIFICATE_VERIFY_FAILED on macOS
--------------------------------------

This may be caused by the brew installer for Python not adding the correct certificates.
Please create a py file from the following snippet and execute it with ``python3``.

.. code-block:: python

    # install_certifi.py
    #
    # sample script to install or update a set of default Root Certificates
    # for the ssl module.  Uses the certificates provided by the certifi package:
    #       https://pypi.python.org/pypi/certifi

    import os
    import os.path
    import ssl
    import stat
    import subprocess
    import sys

    STAT_0o775 = ( stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
                 | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP
                 | stat.S_IROTH |                stat.S_IXOTH )


    def main():
        openssl_dir, openssl_cafile = os.path.split(
            ssl.get_default_verify_paths().openssl_cafile)

        print(" -- pip install --upgrade certifi")
        subprocess.check_call([sys.executable,
            "-E", "-s", "-m", "pip", "install", "--upgrade", "certifi"])

        import certifi

        # change working directory to the default SSL directory
        os.chdir(openssl_dir)
        relpath_to_certifi_cafile = os.path.relpath(certifi.where())
        print(" -- removing any existing file or link")
        try:
            os.remove(openssl_cafile)
        except FileNotFoundError:
            pass
        print(" -- creating symlink to certifi certificate bundle")
        os.symlink(relpath_to_certifi_cafile, openssl_cafile)
        print(" -- setting permissions")
        os.chmod(openssl_cafile, STAT_0o775)
        print(" -- update complete")

    if __name__ == '__main__':
        main()


Source: https://stackoverflow.com/questions/44649449/brew-installation-of-python-3-6-1-ssl-certificate-verify-failed-certificate/44649450#44649450
