from django.core.management.base import BaseCommand, CommandError
from . import _util
import os
import csv
from project.api.models import Color


class Command(BaseCommand):
    def handle(self, *args, **options):
        _util.download_packages(('colors', ), self.stdout)
        self._process_colors()
        _util.delete_temp_dir()

    def _process_colors(self):
        self.stdout.write("Processing colors")
        if not os.path.isfile(_util.get_target_file_path_for_package("colors")):
            self.stderr.write("Colors file does not exist; cannot proceed with processing colors")
            return

        try:
            colors = Color.objects.all()
            colors_by_id = {c.id: c for c in colors}
            with open(_util.get_target_file_path_for_package("colors")) as f:
                reader = csv.DictReader(f)
                changed = {
                    'name': 0,
                    'rgb': 0,
                    'is_trans': 0
                }
                added = 0
                for row in reader:
                    # each row is id,name,rgb,is_trans
                    row_id = int(row['id'])
                    color = colors_by_id.get(row_id)
                    row_is_trans = row['is_trans'] == 't'
                    if color is None:
                        color = Color(id=row_id, name=row['name'], rgb=row['rgb'], is_trans=row_is_trans)
                        added += 1
                    elif color.name == row['name'] and color.rgb == row['rgb'] and color.is_trans == row_is_trans:
                        continue
                    else:
                        for k in ('name', 'rgb', 'is_trans'):
                            if getattr(color, k) != row[k]:
                                setattr(color, k, row[k])
                                changed[k] += 1
                    color.save()
                self.stdout.write("   Added %s new colors" % added)
                self.stdout.write("   Changed %s colors" % sum(changed.values()))
                if sum(changed.values()) > 0:
                    self.stdout.write("      name: %s" % changed['name'])
                    self.stdout.write("      rgb: %s" % changed['rgb'])
                    self.stdout.write("      is_trans: %s" % changed['is_trans'])
        except IOError as error:
            self.stderr.write("Failed opening file; cannot proceed with processing colors")
        self.stdout.write("   Done!")
