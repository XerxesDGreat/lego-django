from . import _util
import os
import csv
from django.core.management.base import CommandError  # maybe use a different error?
from project.api.models import Set, SetTheme, Color
from tqdm import tqdm


class BaseImporter(object):
    """
    Base class for individual import operations.

    Each package is considered its own import operation due to the fact that,
    while the operations and configs are very similar, they ultimately are different.
    """
    dependencies = None

    ####################################
    # Need to implement
    ####################################

    def _parse_row(self, row):
        raise NotImplementedError

    ####################################
    # Public interface
    ####################################
    def __init__(self, package, model, id_key='id', output_writer=None, error_writer=None):
        self.package = package
        self.model = model
        self.id_key = id_key
        self.output_writer = output_writer
        self.error_writer = error_writer

    def do_import(self, fetch_images=True):
        self.download_files()
        self.assert_file_package_exists()

        processed = 0
        added = 0
        changed = {}

        rows, fieldnames = self.get_rows_for_package()
        for row in tqdm(rows):
            props = self._parse_row(row)
            if len(changed.keys()) == 0:
                changed = {k: 0 for k in props.keys()}
            item, was_created = self.get_item(row_details=props)
            if fetch_images:
                item = self.add_image_url(item)
            should_save = False
            if was_created:
                added += 1
                should_save = True
            else:
                for k, v in props.items():
                    if k == self.id_key:
                        continue
                    if getattr(item, k) != v:
                        setattr(item, k, v)
                        changed[k] += 1
                        should_save = True
            if should_save:
                self.save_item(item)
            processed += 1

        self.delete_files()

        return processed, added, changed

    def add_image_url(self, item):
        return item

    def get_rows_for_package(self):
        try:
            with open(_util.get_target_file_path_for_package(self.package)) as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        except IOError as e:
            raise CommandError('Encountered error parsing file: %s' % e.strerror)

        return rows, reader.fieldnames

    def get_queryset(self):
        return self.model.objects.all()

    def get_item(self, package=None, row_details={}, item_id=None, create=True):
        created = False
        package = package or self.package
        cached_list = _util.get_cached_list(list_name=package, queryset=self.get_queryset(), id_key=self.id_key)
        if item_id is None:
            search_id = row_details.get(self.id_key)
        else:
            search_id = item_id
        item = cached_list.get(search_id)
        if item is None and create:
            item = self.model(**row_details)
            created = True
        return item, created

    def save_item(self, item):
        item.save()
        _util.put_to_cached_list(self.package, item, self.id_key)

    def download_files(self):
        _util.download_packages((self.package,), self._write)

    def delete_files(self):
        _util.delete_temp_dir()

    def assert_file_package_exists(self):
        if not os.path.isfile(_util.get_target_file_path_for_package(self.package)):
            raise CommandError("%s.csv file does not exist; cannot proceed with processing" % self.package)

    def _write(self, msg, ending='\n'):
        try:
            self.output_writer.write(msg, ending=ending)
            self.output_writer.flush()
        except Exception as e:
            print(e)
            pass

    def _error(self, msg, ending='\n'):
        try:
            self.error_writer.write(msg, ending=ending)
            self.error_writer.flush()
        except:
            pass


class SetThemeImporter(BaseImporter):
    """
    Import manager for Set themes.
    """

    def __init__(self, *args, **kwargs):
        super(SetThemeImporter, self).__init__(
            package='themes',
            model=SetTheme,
            **kwargs
        )

    def _parse_row(self, row):
        parent = None
        if row['parent_id'] != '':
            parent_id = int(row['parent_id'])
            parent = self.get_item(item_id=parent_id, create=False)[0]
        return {
            'id': int(row['id']),
            'name': row['name'],
            'parent': parent
        }


class SetImporter(BaseImporter):
    """
    Import manager for Sets
    """

    set_url = 'https://rebrickable.com/api/v3/lego/sets/%s/'
    dependencies = ['themes']

    def __init__(self, *args, **kwargs):
        super(SetImporter, self).__init__(
            package='sets',
            model=Set,
            id_key='set_num',
            **kwargs
        )

    def _parse_row(self, row):
        # set_num,name,year,theme_id,num_parts
        theme = SetTheme.objects.get(pk=row['theme_id'])
        return {
            'set_num': row['set_num'],
            'name': row['name'],
            'year': int(row['year']),
            'theme': theme
        }

    def add_image_url(self, item):
        if item and item.image_url is not None:
            return item
        item.image_url = self._fetch_image_for_set_num(item.set_num)
        return item

    def _fetch_image_for_set_num(self, set_num):
        set_info = _util.api_get(self.set_url % set_num, err_logger=self.error_writer)
        if set_info is None:
            return None
        return set_info.get('set_img_url')


class ColorImporter(BaseImporter):
    """
    Importer for color data
    """
    def __init__(self, *args, **kwargs):
        super(ColorImporter, self).__init__(
            package='colors',
            model=Color,
            **kwargs
        )

    def _parse_row(self, row):
        # each row is id,name,rgb,is_trans
        return {
            'id': int(row['id']),
            'name': row['name'],
            'rgb': row['rgb'],
            'is_trans': row['is_trans'] == 't'
        }
