# Intro

This tutorial shows step by step how to use FastAPI with classes.

Each section gradually builds on the previous ones, but it's structured to separate topics, so that you can go directly
to any specific one to solve your specific API needs.

It is also built to work as a future reference.

So you can come back and see exactly what you need.

## Install **FastAPI**

The first step is to install FastAPI.

For the tutorial, you might want to install it with all the optional dependencies and features:

```sh
pip install "fastapi[all]"
```

...that also includes `uvicorn`, that you can use as the server that runs your code.

!!! note

    You can also install it part by part.

    This is what you would probably do once you want to deploy your application to production:
    
    
    ```
    pip install fastapi
    ```

    Also install uvicorn to work as the server:
    
    
    ```
    pip install "uvicorn[standard]"
    ```

    And the same for each of the optional dependencies that you want to use.

## Install **FastAPI Class Based**

The second step is to install FastAPI Class Based:

```bash
pip install class-based-fastapi
```