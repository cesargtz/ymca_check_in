# -*- coding: utf-8 -*-
{
    'name': "ymca chek in",

    'description': """
        Muestra el historial de horas de entrada de los usuarios.
    """,

    'author': "Cesar Gtz",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        'views/resources.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
}
