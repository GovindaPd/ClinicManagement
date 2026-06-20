from django.core.management.base import BaseCommand
from cities_light.models import City, Region, SubRegion
from unidecode import unidecode

class Command(BaseCommand):
    help = "Clean and normalize city and region names in the database"
    # first populate data in model run belo command
    # python manage.py cities_light
    # then run this command to clean data
    # python manage.py clean_cities_data
    
    def handle(self, *args, **options):
        # Clean City names
        cities = City.objects.all()
        for city in cities:
            city.alternate_names = unidecode(city.alternate_names)
            cleaned_name = unidecode(city.name).replace(',', '')

            if city.name != cleaned_name:
                city.name = cleaned_name

            city.save()

        # Clean Region names
        regions = Region.objects.all()
        for region in regions:
            region.alternate_names = unidecode(region.alternate_names)
            cleaned_name = unidecode(region.name).replace(',', '')
            
            if region.name != cleaned_name:
                region.name = cleaned_name
                self.stdout.write(f"Updated region: {region.name}")

            region.save()

        # Clean SubRegion names
        subregions = SubRegion.objects.all()
        for subregion in subregions:
            subregion.alternate_names = unidecode(subregion.alternate_names)
            cleaned_name = unidecode(subregion.name).replace(',', '')

            if subregion.name != cleaned_name:
                subregion.name = cleaned_name

            subregion.save()

        self.stdout.write(self.style.SUCCESS("Successfully cleaned city, region, and subregion names."))