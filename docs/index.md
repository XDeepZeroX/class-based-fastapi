<p align="center">
    <em>Class based routing for FastAPI</em>
</p>
<p align="center">
<img src="https://img.shields.io/github/last-commit/XDeepZeroX/class-based-fastapi.svg">
<br />
<a href="https://pypi.org/project/fastapi-utils" target="_blank">
    <img src="https://img.shields.io/pypi/v/class-based-fastapi?label=class-based-fastapi" alt="Package version">
</a>
    <img src="https://img.shields.io/badge/python-3.6%20--%203.10-blue">
    <img src="https://img.shields.io/github/license/XDeepZeroX/class-based-fastapi">
</p>

---

**Documentation**:
<a href="https://XDeepZeroX.github.io/class-based-fastapi" target="_blank">https://XDeepZeroX.github.io/class-based-fastapi</a>

**Source Code**:
<a href="https://github.com/XDeepZeroX/class-based-fastapi" target="_blank">https://github.com/XDeepZeroX/class-based-fastapi</a>

---

<a href="https://fastapi.tiangolo.com">FastAPI</a> is a modern, fast web framework for building APIs with Python 3.6+.

---

## Features

Write Fast API Controllers (Classes) that can inherit route information from it's parent.

- This also allows to create a path prefix from a template and add api version information in the template.
- You don't need to duplicate the code, you can inherit it.
- To generate OpenAPI documentation, you do not need to explicitly specify the type of the return value, use Generics !

!!! hint

    Do the same with API methods as before, only more convenient.

See the [docs](https://XDeepZeroX.github.io/class-based-fastapi) for more details and examples.

## Requirements

This package is intended for use with any recent version of FastAPI (depending on `pydantic>=1.8.2`), and Python 3.6+.

## Installation

```sh
pip install class-based-fastapi
```

[Next steps >>>](guides/install.md)

## License

This project is licensed under the terms of
the [MIT](https://github.com/XDeepZeroX/class-based-fastapi/blob/main/LICENSE) license.