import random
from django.core.management.base import BaseCommand
from faker import Faker
from projectsheets.models import ProjectSheet

fake = Faker()


class Command(BaseCommand):
    help = "Seed database with fake ProjectSheet data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=20,
            help="Number of ProjectSheet records to create",
        )

    def handle(self, *args, **options):
        count = options["count"]

        languages = [choice[0] for choice in ProjectSheet.LANGUAGE_CHOICES]

        for _ in range(count):
            ProjectSheet.objects.create(
                language=random.choice(languages),
                project_number=f"PRJ-{fake.unique.random_int(1000, 9999)}",
                heading=fake.sentence(nb_words=5),
                project_title=fake.catch_phrase(),
                country=fake.country(),
                location=fake.city(),
                client_info=fake.company() + ", " + fake.address(),
                financier=fake.company(),
                object_name=fake.word().capitalize(),

                performance_short="\n".join(fake.sentences(3)),
                task_description=fake.paragraph(nb_sentences=5),
                performance_description=fake.paragraph(nb_sentences=8),

                date_from=fake.date_between(start_date="-5y", end_date="-2y"),
                date_until=fake.date_between(start_date="-2y", end_date="today"),
                processing_periods_months=random.randint(6, 36),

                total_fee=f"{random.randint(100, 500)}k EUR",
                fee_kocks=f"{random.randint(50, 200)}k EUR",
                fee_planning=f"{random.randint(30, 150)}k EUR",
                fee_construction=f"{random.randint(20, 100)}k EUR",

                tech_value_header="Length\nWidth\nCapacity",
                tech_value_text=f"{random.randint(10,100)} km\n{random.randint(5,20)} m\n{random.randint(1,10)} MTPA",

                staff_total=random.randint(5, 50),
                staff_kocks=random.randint(2, 20),
                senior_staff_names=", ".join(fake.name() for _ in range(3)),

                man_months_total=random.uniform(10, 120),
                man_months_kocks=random.uniform(5, 60),

                partner_companies=", ".join(fake.company() for _ in range(2)),
                captions="\n".join(fake.sentence() for _ in range(3)),
            )

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {count} ProjectSheet records")
        )
