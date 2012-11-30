To run these tests, make sure a test db is setup:
  python manage.py syncdb --all

Create the admin user as per the above account credentials

Run geoserver and django. Make sure that geonode.upload is in INSTALLED_APPS:

  paver start

While geoserver and django are running, run tests:

  REUSE_DB=1 python manage.py test geonode.upload.integrationtests

The upload tests will load a settings module to allow specification of a postgres
database other than what you might use for other local purposes. The settings
will be applied and then unwound after the testclass is complete. This module is:

  geonode.upload.tests.test_settings

If the `test_settings` or standard django settings do not enable a DB_DATASTORE,
the importer tests that import into the database will not run.

If there are existing layers in the test database, the tests will not run unless
the environment variable `DELETE_LAYERS` is present. For example:

  DELETE_LAYERS= python manage.py test geonode.upload.integrationtests

