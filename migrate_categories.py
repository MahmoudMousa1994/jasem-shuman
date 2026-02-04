#!/usr/bin/env python
"""
Migrate artworks from old categories to new standardized categories
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jasem_site.settings')
django.setup()

from gallery.models import Category, Artwork

# Mapping from old category names to new ones
mappings = {
    'Original Paintings': 'original_painting',
    'Original Sculpture': 'original_sculpture',
    'Printed Paintings': 'signed_print_painting',
    'Signed Set of Printed Images of Sculpture': 'signed_print_sculpture'
}

print("Starting category migration...\n")

updated = 0
for old_name, new_name in mappings.items():
    old_cat = Category.objects.filter(name=old_name).first()
    new_cat = Category.objects.filter(name=new_name).first()
    
    if old_cat and new_cat:
        count = Artwork.objects.filter(category=old_cat).update(category=new_cat)
        updated += count
        print(f'✓ Moved {count} artworks from "{old_name}" to "{new_name}"')
    elif old_cat and not new_cat:
        print(f'✗ Warning: Old category "{old_name}" exists but new category "{new_name}" not found')
    elif not old_cat:
        print(f'  Skipped: Old category "{old_name}" not found')

print(f'\nTotal artworks updated: {updated}')

# Now delete old categories
print("\nDeleting old categories...")
old_cats = Category.objects.filter(name__in=mappings.keys())
if old_cats.exists():
    deleted_count, _ = old_cats.delete()
    print(f'✓ Deleted {deleted_count} old categories')
else:
    print('  No old categories to delete')

print('\nFinal categories in database:')
for cat in Category.objects.all():
    artwork_count = Artwork.objects.filter(category=cat).count()
    print(f'  - {cat.name}: "{cat.display_name}" ({artwork_count} artworks)')

print("\nMigration complete!")
