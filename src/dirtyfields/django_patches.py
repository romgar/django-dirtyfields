"""
Override some of the core classes of django

"""
import logging
import django.db.models.query
from .dirtyfields import DirtyFieldsMixin


log = logging.getLogger(__name__)


# NOTE: Overridden to pass the flag to disable dirtyfields for the related objects
# Additions are surrounded by ### comment blocks
class RelatedPopulator(django.db.models.query.RelatedPopulator):

    def populate(self, row, from_obj):

        ###
        # Get the flag from the object
        dirtyfields_disabled = from_obj._dirtyfields_disabled
        ###

        if self.reorder_for_init:
            obj_data = self.reorder_for_init(row)
        else:
            obj_data = row[self.cols_start:self.cols_end]
        if obj_data[self.pk_idx] is None:
            obj = None
        else:
            ###
            # Pass disable_dirtyfield only if it's a subclass of DirtyFieldsMixin
            # because only a subclass of DirtyFieldsMixin will support this kwarg
            if issubclass(self.model_cls, DirtyFieldsMixin):
                obj = self.model_cls.from_db(
                    self.db, self.init_list, obj_data,
                    # Pass disable_dirtyfields
                    disable_dirtyfields=dirtyfields_disabled
                )
            else:
                if dirtyfields_disabled:
                    log.warning(
                        f'Dirtyfields is disabled but this model does not '
                        f'support it: {self.model_cls} '
                        f'=> Inherit from DirtyFieldsMixin to support it'
                    )
                obj = self.model_cls.from_db(self.db, self.init_list, obj_data)
            ###

        if obj and self.related_populators:
            for rel_iter in self.related_populators:
                rel_iter.populate(row, obj)
        setattr(from_obj, self.cache_name, obj)
        if obj and self.reverse_cache_name:
            setattr(obj, self.reverse_cache_name, from_obj)


# NOTE: Overridden to use our RelatedPopulator
def get_related_populators(klass_info, select, db):
    iterators = []
    related_klass_infos = klass_info.get('related_klass_infos', [])
    for rel_klass_info in related_klass_infos:
        ###
        # Use our RelatedPopulator
        rel_cls = RelatedPopulator(rel_klass_info, select, db)
        ###
        iterators.append(rel_cls)
    return iterators


# NOTE: Overridden to pass the flag to disable dirtyfields from the queryset to the model creation
# Additions are surrounded by ### comment blocks
class ModelIterable(django.db.models.query.ModelIterable):

    def __iter__(self):
        queryset = self.queryset

        ###
        # Get disable_dirtyfields from the queryset
        disable_dirtyfields = queryset._disable_dirtyfields
        ###

        db = queryset.db
        compiler = queryset.query.get_compiler(using=db)
        # Execute the query. This will also fill compiler.select, klass_info,
        # and annotations.
        results = compiler.execute_sql(chunked_fetch=self.chunked_fetch)
        select, klass_info, annotation_col_map = (compiler.select, compiler.klass_info,
                                                  compiler.annotation_col_map)
        model_cls = klass_info['model']
        select_fields = klass_info['select_fields']
        model_fields_start, model_fields_end = select_fields[0], select_fields[-1] + 1
        init_list = [f[0].target.attname
                     for f in select[model_fields_start:model_fields_end]]
        related_populators = get_related_populators(klass_info, select, db)
        for row in compiler.results_iter(results):

            ###
            # Pass disable_dirtyfield only if it's a subclass of DirtyFieldsMixin
            # because only a subclass of DirtyFieldsMixin will support this kwarg
            if issubclass(model_cls, DirtyFieldsMixin):
                obj = model_cls.from_db(
                    db, init_list, row[model_fields_start:model_fields_end],
                    # Pass disable_dirtyfields
                    disable_dirtyfields=disable_dirtyfields
                )
            else:
                if disable_dirtyfields:
                    log.warning(
                        f'Dirtyfields is disabled but this model does not '
                        f'support it: {model_cls} '
                        f'=> Inherit from DirtyFieldsMixin to support it'
                    )
                obj = model_cls.from_db(db, init_list, row[model_fields_start:model_fields_end])
            ###

            if related_populators:
                for rel_populator in related_populators:
                    rel_populator.populate(row, obj)
            if annotation_col_map:
                for attr_name, col_pos in annotation_col_map.items():
                    setattr(obj, attr_name, row[col_pos])

            # Add the known related objects to the model, if there are any
            if queryset._known_related_objects:
                for field, rel_objs in queryset._known_related_objects.items():
                    # Avoid overwriting objects loaded e.g. by select_related
                    if hasattr(obj, field.get_cache_name()):
                        continue
                    pk = getattr(obj, field.get_attname())
                    try:
                        rel_obj = rel_objs[pk]
                    except KeyError:
                        pass  # may happen in qs1 | qs2 scenarios
                    else:
                        setattr(obj, field.name, rel_obj)

            yield obj
