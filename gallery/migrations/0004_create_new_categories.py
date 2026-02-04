# Generated manually for category restructuring

from django.db import migrations


def create_categories(apps, schema_editor):
    """Create the 4 new categories for the restructured system"""
    Category = apps.get_model('gallery', 'Category')
    
    categories = [
        {
            'name': 'original_painting',
            'display_name': 'Original Painting',
            'description': 'One-of-a-kind original paintings by Jasem Shuman'
        },
        {
            'name': 'original_sculpture',
            'display_name': 'Original Sculpture',
            'description': 'Unique original sculptures by Jasem Shuman'
        },
        {
            'name': 'signed_print_painting',
            'display_name': 'Signed Printed Painting',
            'description': 'Limited edition signed prints of original paintings'
        },
        {
            'name': 'signed_print_sculpture',
            'display_name': 'Signed Set of Printed Images of Sculpture',
            'description': 'Limited edition signed photograph sets showcasing sculptures from multiple angles'
        },
    ]
    
    for cat_data in categories:
        Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'display_name': cat_data['display_name'],
                'description': cat_data['description']
            }
        )


def reverse_categories(apps, schema_editor):
    """Remove the new categories"""
    Category = apps.get_model('gallery', 'Category')
    Category.objects.filter(
        name__in=[
            'original_painting',
            'original_sculpture', 
            'signed_print_painting',
            'signed_print_sculpture'
        ]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0003_remove_artwork_original_available_and_more'),
    ]

    operations = [
        migrations.RunPython(create_categories, reverse_categories),
    ]
