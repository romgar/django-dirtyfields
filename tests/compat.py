
def get_model_name(klass):
    if hasattr(klass._meta, 'model_name'):
        model_name = klass._meta.model_name
    else:  # Django < 1.6
        model_name = klass._meta.module_name

    return model_name
