
def setup(app):
    """
    Mandatory to cross ref any non-default sphinx behaviours defined in Django
    Thanks https://reinout.vanrees.org/weblog/2012/12/01/django-intersphinx.html
    We can then use :django:settings:`ROOT_URLCONF` for example
    (We then avoid ERROR: Unknown interpreted text role "django:settings")
    """
    app.add_crossref_type(
        directivename="setting",
        rolename="setting",
        indextemplate="pair: %s; setting",
    )
    app.add_crossref_type(
        directivename="templatetag",
        rolename="ttag",
        indextemplate="pair: %s; template tag"
    )
    app.add_crossref_type(
        directivename="templatefilter",
        rolename="tfilter",
        indextemplate="pair: %s; template filter"
    )
    app.add_crossref_type(
        directivename="fieldlookup",
        rolename="lookup",
        indextemplate="pair: %s; field lookup type",
    )
