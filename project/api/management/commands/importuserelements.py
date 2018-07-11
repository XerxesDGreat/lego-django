from django.core.management.base import BaseCommand, CommandError
import os
import csv
from project.api.models import Element, Part, Color, UserElement
from django.contrib.auth.models import User
from ._util import api_get


class Command(BaseCommand):
    thumbnail_url_pattern = "https://rebrickable.com/api/v3/lego/parts/%s/colors/%s/"

    def add_arguments(self, parser):
        # positional args
        parser.add_argument('user_element_file_path', help="file path to the user element csv")

    def handle(self, *args, **options):
        if not os.path.isfile(options['user_element_file_path']):
            raise CommandError("user element file %s does not exist" % options['user_element_file_path'])

        user = User.objects.get(id=1)

        with open(options['user_element_file_path']) as f:
            reader = csv.DictReader(f)
            for row in reader:
                # format is Part,Color,Quantity
                quantity = int(row['Quantity'])
                color = Color.objects.get(id=int(row['Color']))
                part = Part.objects.get(part_num=row['Part'])
                try:
                    element = Element.objects.get(color=color, part=part)
                    if element.image_url == '':
                        self.stdout.write("updating element details for %s:%s" % (part.part_num, color.id))
                        thumbnail, lego_element_id = self._get_element_details_for_part_and_color_from_api(part, color)
                        element.image_url = thumbnail
                        element.lego_element_id = lego_element_id
                        element.save()
                except Element.DoesNotExist:
                    self.stdout.write("creating element for %s:%s" % (part.part_num, color.id))
                    thumbnail, lego_element_id = self._get_element_details_for_part_and_color_from_api(part, color)
                    element = Element(color=color, part=part, image_url=thumbnail, lego_element_id=lego_element_id)
                    element.save()
                except Element.MultipleObjectsReturned:
                    self.stderr.write("more than one element exists for part %s and color %s; continuing"
                                      % (part.part_num, color.id))
                    continue

                if element is None:
                    continue

                try:
                    user_element = UserElement.objects.get(element=element)
                    if user_element.quantity_in_storage != quantity:
                        self.stdout.write("updating userelement")
                        user_element.quantity_in_storage = quantity
                        user_element.save()
                except UserElement.DoesNotExist:
                    self.stdout.write("creating userelement")
                    # most likely
                    user_element = UserElement(user=user, element=element, quantity_on_display=0,
                                               quantity_in_storage=quantity)
                    user_element.save()
                except UserElement.MultipleObjectsReturned:
                    self.stderr.write("more than one userelement exists for part %s and color %s; continuing"
                                      % (part.part_num, color.id))
                    continue
        self.stdout.write("done")

    def _get_element_details_for_part_and_color_from_api(self, part, color):
        url = self.thumbnail_url_pattern % (part.part_num, color.id)
        response = api_get(url, err_logger=self.stderr.write)
        if response is None:
            return '', ''

        thumbnail_maybe = response.get('part_img_url', None)
        thumbnail = '' if thumbnail_maybe is None else thumbnail_maybe
        elements = response.get('elements', [])
        element = '' if len(elements) == 0 else elements[0]
        return thumbnail, element


    #     find_element_query = "SELECT id FROM api_element WHERE part_id=? AND color_id=?"
    #     find_user_element_query = "SELECT * FROM api_userelement WHERE element_id=? AND user_id=?"
    #     update_element_query = """UPDATE api_userelement
    # SET updated=?, quantity_in_storage=?, quantity_on_display=0
    # WHERE user_id=? AND element_id=?"""
    #     add_element_query = """INSERT INTO api_userelement (element_id, user_id, quantity_in_storage, quantity_on_display, created, updated)
    # VALUES (?,?,?,?,?,?)"""
    #     with open('/Users/josh/Downloads/rebrickable_parts_xerxesdgreat.csv') as f:
    #         with open('/Users/josh/tmp/failed_elements.csv', 'w') as y:
    #             # Part,Color,Quantity
    #             r = csv.DictReader(f)
    #             counter = 0
    #             for row in r:
    #                 q = row['Quantity']
    #                 t = (row['Part'], row['Color'])
    #                 _ = c.execute(find_element_query, t)
    #                 element = c.fetchone()
    #                 if element is None:
    #                     print("No element found for part %s in color %s" % t)
    #                     y.write(','.join(t))
    #                     continue
    #                 id = element['id']
    #                 _ = c.execute(find_user_element_query, (element['id'], 1))
    #                 userelement = c.fetchone()
    #                 now = datetime.datetime.now()
    #                 if userelement is not None:
    #                     _ = c.execute(update_element_query, (now, q, 1, id))
    #                 else:
    #                     _ = c.execute(add_element_query, (id, 1, q, 0, now, now))
    #                 if c.rowcount == 0:
    #                     print("Failed to insert/update user element")
    #                     y.write(','.join(t))
    #                     continue
    #                 conn.commit()
    #                 counter += 1
    #                 if counter % 100 == 0:
    #                     print('.', end='', flush=True)