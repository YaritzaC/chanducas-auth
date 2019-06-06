from flask.globals import _app_ctx_stack, _request_ctx_stack
from werkzeug.urls import url_parse
from werkzeug.exceptions import NotFound


def split_url(url, method='GET'):
    """Devuelve el nombre del punto final y los argumentos que coinciden con una URL
    determinada. En otras palabras, esto es lo contrario de url_for () de Flask.
    """
    appctx = _app_ctx_stack.top
    reqctx = _request_ctx_stack.top
    if appctx is None:
        raise RuntimeError('Intento hacer coincidir una URL sin el'
                           'contexto de aplicación siendo empujado. Esto tiene que ser'
                           'ejecutado cuando el contexto de la aplicación está disponible.')

    if reqctx is not None:
        url_adapter = reqctx.url_adapter
    else:
        url_adapter = appctx.url_adapter
        if url_adapter is None:
            raise RuntimeError('La aplicación no pudo crear una URL'
                               'apdaptada para la coincidencia de URL independiente de la solicitud.'
                               'Es posible que puedas solucionar este problema configurando'
                               'la variable SERVER_NAME config.')
    parsed_url = url_parse(url)
    if parsed_url.netloc is not '' and \
                    parsed_url.netloc != url_adapter.server_name:
        raise ValidationError('Invalid URL: ' + url)
    try:
        result = url_adapter.match(parsed_url.path, method)
    except NotFound:
        raise ValidationError('Invalid URL: ' + url)
    return result
