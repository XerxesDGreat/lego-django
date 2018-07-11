from django.core.management.base import BaseCommand, CommandError
import requests
import os
import csv
from project.api.models import Part, PartCategory
import time
from . import _util


class Command(BaseCommand):
    help = "Fetches and imports the database for sets and parts"

    base_link = 'https://m.rebrickable.com/media/downloads/'
    tmp_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '.downloads')
    packages = [
        'part_categories',
        'parts',
    ]

    api_key = '7a63f7230da51d57ede0d83357d160d9'
    part_color_url = "https://rebrickable.com/api/v3/lego/parts/%s/colors"

    part_category_cache = None

    def _get_part_categories(self):
        if self.part_category_cache is None:
            part_categories = PartCategory.objects.all()
            self.part_category_cache = {str(pc.id): pc for pc in part_categories}

        return self.part_category_cache

    def handle(self, *args, **options):
        self._download_files()
        self._process_part_categories()
        self._process_parts()
        self._delete_files()

    def _process_part_categories(self):
        """
        Processes the downloaded part categories, updating the database as needed.

        Goes through the downloaded part categories list and determines if there's anything
        which needs to be updated. If so, add the new categories to the database.
        :return:
        """
        self.stdout.write("Processing part categories")
        if not os.path.isfile(_util.get_target_file_path_for_package("part_categories")):
            self.stderr.write("Part category file does not exist; cannot proceed with processing part categories")
            return

        try:
            with open(_util.get_target_file_path_for_package("part_categories")) as f:
                reader = csv.DictReader(f)
                changed = 0
                added = 0
                for row in reader:
                    # each row is id,name
                    part_category = self._get_part_categories().get(row['id'], None)
                    if part_category is None:
                        part_category = PartCategory(id=row['id'], name=row['name'])
                        added += 1
                    elif part_category.name != row['name']:
                        part_category.name = row['name']
                        changed += 1
                    else:
                        continue
                    part_category.save()
                self.stdout.write("   Added %s new part categories" % added)
                self.stdout.write("   Changed %s part categories" % changed)
        except IOError as error:
            self.stderr.write("Failed opening file; cannot proceed with processing part categories")
        self.stdout.write("   Done!")

    def _process_parts(self):
        """
        Processes the downloaded parts, updating the database as needed.
        :return:
        """
        self.stdout.write("Processing parts")

        if not os.path.isfile(_util.get_target_file_path_for_package("parts")):
            self.stderr.write("Part file does not exist; cannot proceed with processing parts")
            return

        parts = Part.objects.all()
        parts_by_id = {part.part_num: part for part in parts}

        try:
            with open(_util.get_target_file_path_for_package("parts")) as f:
                reader = csv.DictReader(f)
                changed_name = 0
                changed_category = 0
                added = 0
                for row in reader:
                    # each row is part_num,name,part_cat_id
                    part = parts_by_id.get(row['part_num'], None)
                    part_category = self._get_part_categories().get(row['part_cat_id'])
                    if part is None:
                        part = Part(part_num=row['part_num'], name=row['name'], category=part_category)
                        part.thumbnail = self._get_thumbnail_from_api(part.part_num)
                        added += 1
                    elif part.name == row['name'] and part.category == part_category:
                        # no meaningful change
                        continue
                    else:
                        if part.name != row['name']:
                            part.name = row['name']
                            changed_name += 1
                        if part.category != part_category:
                            part.category = part_category
                            changed_category += 1
                    part.save()
                self.stdout.write("   Added %s new parts" % added)
                self.stdout.write("   Changed %s names" % changed_name)
                self.stdout.write("   Changed %s categories" % changed_category)

        except IOError as error:
            self.stderr.write("Failed opening file; cannot proceed with processing parts")
        self.stdout.write("   Done!")

    def _get_thumbnail_from_api(self, part_num):
        self.stdout.write('fetching thumbnail for %s' % part_num)

        # we have a 2 calls-per-second limit; make sure we honor that
        time.sleep(1)

        url = self.part_color_url % part_num
        element_response = requests.get(url, params={"key": self.api_key})
        if element_response.status_code != 200:
            self.stdout.write('no results for element call for part %s; got status %s (url: %s)' %
                              (part_num, element_response.status_code, url))
            return ""

        element_json = element_response.json()
        if element_json['count'] == 0:
            self.stdout.write("empty element list; no image for %s" % part_num)
            return ""
        else:
            img_url = None
            for r in element_json['results']:
                if img_url is None or r['color_id'] != -1:
                    img_url = r['part_img_url']
                    if r['color_id'] != -1:
                        break
            return img_url if img_url is not None else ""

    def _download_files(self):
        _util.download_packages(self.packages, self.stdout)

    def _delete_files(self):
        _util.delete_temp_dir()
