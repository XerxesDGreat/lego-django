from django.core.management.base import BaseCommand, CommandError
from . import _importers


class Command(BaseCommand):
    help = "Fetches and imports data from the Bricklink API"
    available_packages = {
        'themes': _importers.SetThemeImporter,
        'sets': _importers.SetImporter,
        'colors': _importers.ColorImporter
    }

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument('packages',
                            nargs='+',
                            help='List of packages to import, ordered in the order in which they should be installed ' +
                                 '(dependencies first)',
                            choices=self.available_packages.keys())
        parser.add_argument('--ignore-dependencies',
                            help='Executes update without testing that dependencies are updated as well',
                            action='store_true')
        parser.add_argument('--skip-images',
                            help='Imports items without attempting to download images from the API',
                            action='store_true')

    def handle(self, *args, **options):
        packages = options['packages']
        self._meets_dependency_requirements(package_list=packages, ignore_dependencies=options['ignore_dependencies'])
        for package in packages:
            self.stdout.write("Processing package %s... " % package, ending='')
            package_importer_cls = self.available_packages.get(package)
            if package_importer_cls is None:
                raise CommandError("Missing package importer for package [%s]" % package)
            package_importer = package_importer_cls(output_writer=self.stdout, error_writer=self.stderr)

            processed, added, changed = package_importer.do_import(fetch_images=(not options['skip_images']))
            self.stdout.write(self.style.SUCCESS('Done!'))
            self.stdout.write('  processed: %s, added: %s, changed fields: %s' %
                              (processed, added, sum(changed.values())))

    def _meets_dependency_requirements(self, package_list=[], ignore_dependencies=False):
        for package in package_list:
            package_class = self.available_packages.get(package)
            if package_class.dependencies is None:
                continue
            for dependency in package_class.dependencies:
                if dependency in package_list:
                    continue
                msg = 'Missing dependency [%s] for package [%s]' % (dependency, package)
                if ignore_dependencies:
                    full_msg = 'Warning! %s - continuing due to ignore_dependencies flag' % msg
                    self.stdout.write(self.style.WARNING(full_msg))
                else:
                    raise CommandError(msg)


