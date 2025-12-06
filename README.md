<div style="text-align: center;">
  <img src="app/static/img/photos/rubikhub-mono.png" alt="RubikHub logo" style="max-height:120px;">
</div>

# RubikHub

RubikHub is an open-access repository of Rubik-related datasets and research artefacts. We provide a friendly platform that integrates a local Zenodo-like service for dataset registration and DOI minting, and tools for dataset management and publication.

This project was developed as part of the EGC course (Evolución y Gestión de la Configuración / Evolution and Configuration Management).

## What we offer

- Public repository of datasets related to Rubik (feature models, datasets, examples).
- Web UI and API endpoints for uploading, versioning and publishing datasets.
- Test suites (unit, integration, selenium) and locust files for load testing.

## Quick links

- Documentation: https://docs.uvlhub.io/

## Contributing and development

If you want to run or contribute to the project locally, check the repository for `requirements.txt` / `pyproject.toml` and the `app` package. Tests and development utilities are included under the `tests` and `app/modules/*/tests` folders.

If you are running Selenium-based tests or the local FakeNODO service, prefer using the testing configuration and an isolated test database. The project includes helper routes and utilities to reset the test database when running automated UI tests.

## Contributors

This project was developed and is maintained by:

- Manuel Nuño
- Mario Benitez
- Juan Antonio Ruiz
- Alejandro Ruiz
- Alejandro Mantecon
- Juan Moreno

