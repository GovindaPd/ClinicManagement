from django.core.management.base import BaseCommand
from cities_light.models import City, Region
from unidecode import unidecode

class Command(BaseCommand):
    help = "Clean and normalize city and region names in the database"

    def handle(self, *args, **options):
        # Clean City names
        cities = City.objects.all()
        for city in cities:
            cleaned_name = unidecode(city.name)
            if city.name != cleaned_name:
                city.name = cleaned_name
                city.save()
                self.stdout.write(f"Updated city: {city.name}")

        # Clean Region names
        # regions = Region.objects.all()
        # for region in regions:
        #     cleaned_name = unidecode(region.name).replace(',', '')
        #     if region.name != cleaned_name:
        #         region.name = cleaned_name
        #         region.save()
        #         self.stdout.write(f"Updated region: {region.name}")

        self.stdout.write(self.style.SUCCESS("Successfully cleaned city and region names."))