from .models import Product


def validate_order_product(content_dict, form_field, errors):
    if form_field not in content_dict.keys():
        errors['required'].append(str(content_dict[form_field]))
    elif content_dict[form_field] is None or content_dict[form_field] == 0:
        errors['empty'].append(str(content_dict[form_field]))
    elif not isinstance(content_dict[form_field], int):
        content_type = type(content_dict[form_field])
        error_text = f'{form_field}: Ожидался {int} со значениями, но был получен {content_type}. '
        errors['type'] += error_text
    elif not content_dict[form_field] > 0:
        error_text = f'{form_field}: Значение поля не может быть отрицательным. '
        errors['type'] += error_text
    return errors


def validate_phonenumber(num):
    pass


def validate_form_field(content_dict, form_field, data_type, errors):
    error_text = ''

    if form_field not in content_dict.keys():
        errors['required'].append(form_field)
    elif content_dict[form_field] is None:
        errors['empty'].append(form_field)
    elif not isinstance(content_dict[form_field], data_type):
        content_type = type(content_dict[form_field])
        error_text = f'{form_field}: Ожидался {data_type} со значениями, но был получен {content_type}. '
        errors['type'] += error_text
    elif len(content_dict[form_field]) == 0:
        if form_field == 'products':
            error_text = 'products: Этот список не может быть пустым.'
            errors['empty_products'] = error_text
        else:
            errors['empty'].append(form_field)
    elif form_field == 'products':
        for product in content_dict['products']:
            errors = validate_order_product(product, 'product', errors)
            errors = validate_order_product(product, 'quantity', errors)
            if not Product.objects.filter(pk=product['product']):
                errors['wrong_products'].append(str(product['product']))
    elif form_field == 'phonenumber':
        number = content_dict[form_field]
        if (len(number) == 11 and number[0:2] == '89') or (len(number) == 12 and number[0:3] == '+79'):
            pass
        else:
            errors['wrong_number'] = 'Некорректный номер телефона'
    return errors


def parse_errors_dict(errors_dict):
    errors = {}
    if errors_dict['required']:
        fields = ', '.join(errors_dict['required'])
        if len(errors_dict['required']) == 1:
            required = fields + ': Обязательное поле.'
        else:
            required = fields + ': Обязательные поля.'
        errors['required fields error'] = required
    if errors_dict['empty']:
        fields = ', '.join(errors_dict['empty'])
        if len(errors_dict['empty']) == 1:
            empty = fields + ': Это поле не может быть пустым.'
        else:
            empty = fields + ': Эти поля не могут быть пустыми.'
        errors['empty fields error'] = empty
    if errors_dict['type']:
        errors['type field error'] = errors_dict['type']
    if errors_dict['empty_products']:
        errors['empty products list error'] = errors_dict['empty_products']
    if errors_dict['wrong_products']:
        products = ', '.join(errors_dict['wrong_products'])
        if len(errors_dict['wrong_products']) == 1:
            wrong = 'Продукт с этим ключём не найден: ' + products + '.'
        else:
            wrong = 'Продукты с этими ключами не найдены: ' + products + '.'
        errors['wrong products error'] = wrong
    if errors_dict['wrong_number']:
        errors['wrong phone error'] = errors_dict['wrong_number']
    return {
        'errors': errors
    }


def order_fields_validate(content_dict, fields):
    errors_dict = {
                'required': [],
                'empty': [],
                'type': '',
                'empty_products': '',
                'wrong_products': [],
                'wrong_number': '',
            }

    for field, data_type in fields:
        errors_dict = validate_form_field(content_dict, field, data_type, errors_dict)

    errors = parse_errors_dict(errors_dict)

    return errors
