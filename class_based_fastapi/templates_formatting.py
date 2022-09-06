from typing import Dict, Any, Type, Tuple

from class_based_fastapi.utilities import snake_case


def _rest_api_naming(name: str) -> str:
    """Преобразование наименования API

    Args:
        name: Исходное название

    Returns: Преобразованное название
    """
    return snake_case(name).replace('_', '-')


def replace_parameter_template(endpoint: Dict[str, Any], mask_parameter: str, old_value: str, new_value: str) -> None:

    template_path = endpoint.args.template_path
    indx_mask = template_path.find(mask_parameter)
    if indx_mask == -1:
        return

    if indx_mask + len(mask_parameter) < len(template_path):
        mask = f'{template_path[indx_mask - 1]}{old_value}{template_path[indx_mask + len(mask_parameter)]}'
        new_mask = f'{template_path[indx_mask - 1]}{new_value}{template_path[indx_mask + len(mask_parameter)]}'
    else:
        mask = f'{template_path[indx_mask - 1]}{old_value}'
        new_mask = f'{template_path[indx_mask - 1]}{new_value}'

    endpoint.args.path = endpoint.args.path.replace(mask, new_mask)


def _replace_child_name_controller(endpoint: Dict[str, Any],
                                   name: str,
                                   base: Type[Any],
                                   attrs: Dict[str, Any]) -> None:
    """Замена унаследованного названия контроллера

    Args:
        endpoint: Информация о методе
        name: Название текущего класса (контроллера)
        base: Тип унаследованного класса
    """
    old_name = _rest_api_naming(base.__name__)
    new_name = _rest_api_naming(name)

    replace_parameter_template(endpoint, '{controller}', old_name, new_name)


def _replace_child_name_module(endpoint: Dict[str, Any],
                               name: str,
                               base: Type[Any],
                               attrs: Dict[str, Any]) -> None:
    """Замена унаследованного названия контроллера

    Args:
        endpoint: Информация о методе
        name: Название текущего класса (контроллера)
        base: Тип унаследованного класса
    """
    new_name = attrs.get('NAME_MODULE')
    if new_name is None:
        return
    old_name = endpoint.args.name_module

    replace_parameter_template(endpoint, '{module}', old_name, _rest_api_naming(new_name))


def _replace_child_varsion_api(endpoint: Dict[str, Any],
                               name: str,
                               base: Type[Any],
                               attrs: Dict[str, Any]) -> None:
    """Замена унаследованного названия контроллера

    Args:
        endpoint: Информация о методе
        name: Название текущего класса (контроллера)
        base: Тип унаследованного класса

    """
    new_name = attrs.get('VERSION_API')
    if new_name is None:
        return
    old_name = endpoint.args.varsion_api

    replace_parameter_template(endpoint, '{version}', old_name, _rest_api_naming(new_name))


def _processing_child_paths(endpoints: Dict[str, Any],
                            name: str,
                            bases: Tuple[Type[Any]],
                            attrs: Dict[str, Any]) -> Dict[str, Any]:
    for base in bases:
        for endpoint in endpoints.values():

            _replace_child_name_controller(endpoint, name, base, attrs)
            _replace_child_name_module(endpoint, name, base, attrs)
            _replace_child_varsion_api(endpoint, name, base, attrs)

    return endpoints
