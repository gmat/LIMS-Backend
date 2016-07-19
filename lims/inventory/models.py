
from django.db import models
from django.contrib.auth.models import User

from mptt.models import MPTTModel, TreeForeignKey


class ItemType(MPTTModel):
    """
    Provides a tree based model of types, each which can have parents/children
    """
    name = models.CharField(max_length=150, unique=True, db_index=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    def has_children(self):
        return True if self.get_descendant_count() > 0 else False

    def display_name(self):
        if self.level > 0:
            return '{} {}'.format('--' * self.level, self.name)
        return self.name

    def root(self):
        if self.parent:
            return self.parent.get_root().name
        return self.name

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class AmountMeasure(models.Model):
    """
    A measurement and corrosponding postfix
    """
    name = models.CharField(max_length=100, unique=True, db_index=True)
    symbol = models.CharField(max_length=10, unique=True, db_index=True)

    def __str__(self):
        return "{} ({})".format(self.name, self.symbol)


class Location(MPTTModel):
    """
    Provides a physical location for an item
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=6, unique=True, null=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    def has_children(self):
        return True if self.get_descendant_count() > 0 else False

    def display_name(self):
        if self.level > 0:
            return '{} {}'.format('--' * self.level, self.name)
        return self.name

    def __str__(self):
        if self.parent:
            return '{} ({})'.format(self.name, self.parent.name)
        return self.name


class Set(models.Model):
    """
    A named set of items in the inventory
    """
    name = models.CharField(max_length=40)
    is_public = models.BooleanField(default=False)
    is_partset = models.BooleanField(default=False)

    def number_of_items(self):
        return self.items.count()

    def __str__(self):
        return self.name


class Item(models.Model):
    """
    Represents an item in a inventory
    """
    name = models.CharField(max_length=200, db_index=True)
    identifier = models.CharField(max_length=128, null=True, blank=True, db_index=True, unique=True)
    description = models.TextField(blank=True, null=True)
    item_type = TreeForeignKey(ItemType)

    tags = models.ManyToManyField(Tag, blank=True)

    in_inventory = models.BooleanField(default=False)
    amount_available = models.IntegerField(default=0)
    amount_measure = models.ForeignKey(AmountMeasure)
    location = TreeForeignKey(Location, null=True, blank=True)

    added_by = models.ForeignKey(User)
    added_on = models.DateTimeField(auto_now_add=True)
    last_updated_on = models.DateTimeField(auto_now=True)

    sets = models.ManyToManyField(Set, related_name='items', blank=True)

    created_from = models.ManyToManyField('self', blank=True, symmetrical=False)

    def get_tags(self):
        return ", ".join([t.name for t in self.tags.all()])

    def location_path(self):
        return ' > '.join([x.name for x in self.location.get_ancestors(include_self=True)])

    def save(self, *args, **kwargs):
        if self.amount_available > 0:
            self.in_inventory = True
        super(Item, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class ItemProperty(models.Model):
    """
    Represents a singular user defined property of an item
    """
    item = models.ForeignKey(Item, related_name='properties')
    name = models.CharField(max_length=200)
    value = models.TextField()

    def __str__(self):
        return self.name


class ItemTransfer(models.Model):
    """
    Represents an amount of item in transfer for task
    """
    item = models.ForeignKey(Item, related_name='transfers')
    amount_taken = models.IntegerField(default=0)
    amount_measure = models.ForeignKey(AmountMeasure)
    run_identifier = models.CharField(max_length=64, blank=True, null=True)
    barcode = models.CharField(max_length=20, blank=True, null=True)
    coordinates = models.CharField(max_length=2, blank=True, null=True)

    date_created = models.DateTimeField(auto_now_add=True)

    # You're adding not taking away
    is_addition = models.BooleanField(default=False)

    transfer_complete = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return '{} {}/{}'.format(self.item.name, self.barcode, self.coordinates)
