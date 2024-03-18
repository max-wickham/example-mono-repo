# Infra Mono

This is an example from a project of using a mono repo both for embedded code and for the backend and frontend apps. This is just a proof on concept and many practices used here should not be used in production code. The repo more shows an example of project structure.

## Backend Design

The entire backend is implemented using Python and FastAPI. This includes both multiple APIs as well as a background task system using celery for AI training jobs and other computationally heavy work. All the different microservices and the frontend are dockerised allowing for easy local development without having to install many dependencies.
