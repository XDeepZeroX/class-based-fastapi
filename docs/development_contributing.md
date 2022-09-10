# Development - Contributing

First, you might want to see the basic ways to [help and get help](get_help.md).

## Developing

Once you’ve cloned the repository, here are some guidelines to set up your environment:

### Create environment

After cloning the repository, you can use create a virtual environment:

```console
~/class-based-fastapi$ python -m venv venv
```

!!! info

    Requires python 3

**Next step:** activate the environment

### Install requirements

After activating the environment, it is required to install all dependencies:

```console
(venv) ~/class-based-fastapi$ pip install -e '.[all]'
```

### Docs

The documentation uses [MkDocs](https://www.mkdocs.org/).

All the documentation is in Markdown format in the directory `./docs`.

Many of the sections in the User Guide have blocks of code.

In fact, those blocks of code are not written inside the Markdown, they are Python files in the `./docs/src/` directory.

And those Python files are included/injected in the documentation when generating the site.

### Docs for tests

Most of the tests actually run against the example source files in the documentation.

This helps making sure that:

* The documentation is up to date.
* The documentation examples can be run as is.
* Most of the features are covered by the documentation, ensured by test coverage.

During local development, there is a script that builds the site and checks for any changes, live-reloading:

```console
(venv) ~/class-based-fastapi$ mkdocs serve
```

It will serve the documentation on [http://127.0.0.1:8000](http://127.0.0.1:8000).

That way, you can edit the documentation/source files and see the changes live.

### Tests

You can run all tests via:

```console
(venv) ~/class-based-fastapi$ py.test
```


