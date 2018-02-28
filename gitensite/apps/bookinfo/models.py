#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from gitenberg.metadata.pandata import Pandata

from django.db import models

logger = logging.getLogger(__name__)

gh_org = 'GITenberg'

def smart_truncate(content, length=100, suffix='...'):
    if len(content) <= length:
        return content
    else:
        return ' '.join(content[:length+1].split(' ')[0:-1]) + suffix

class Author(models.Model):
    name = models.CharField(max_length=255, default="", null=True, blank=True)
    aliases = models.CharField(max_length=255, default="", null=True, blank=True)
    birth_year = models.IntegerField(null=True)
    death_year = models.IntegerField(null=True)
    wikipedia_url = models.URLField(max_length=500)

class Book(models.Model):
    book_id = models.IntegerField()
    repo_name = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=1000, default="", db_index=True)
    language = models.CharField(max_length=5, default="en", null=False, db_index=True)
    description = models.TextField(default="", null=True, blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, db_index=True, null=True)
    gutenberg_type = models.CharField(max_length=255, default="", null=True, blank=True)
    gutenberg_bookshelf = models.CharField(max_length=1000, default="")
    subjects = models.CharField(max_length=1000, default="")
    full_text = models.TextField(default="", null=True, blank=True)
    num_downloads = models.IntegerField(default=0)
    
    added = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)
    
    yaml = models.TextField(null=True, default="")

    def __unicode__(self):
        return self.repo_name

    @property
    def title_short(self):
        return smart_truncate(self.title, 65)

    @property
    def subjects_str(self):
        return self.subjects.replace(";", ", ")
    
    @property
    def author_first_last(self):
        return " ".join(self.author.name.split(", ")[::-1])

    @property
    def description_short(self):
        return smart_truncate(self.description, 300)

    @property
    def repo_url(self):
        return 'https://github.com/{}/{}'.format(gh_org,self.repo_name)

    @property
    def issues_url(self):
        return 'https://github.com/{}/{}/issues'.format(gh_org,self.repo_name)

    @property
    def downloads_url(self):
        return 'https://github.com/{}/{}/releases'.format(gh_org,self.repo_name)

    @property
    def pg_url(self):
        return 'https://www.gutenberg.org/ebooks/{}'.format(self.book_id)

    @property
    def cover_url(self):
        existing_covers = list(Cover.objects.filter(book=self))
        for cover in existing_covers:
            if cover.default_cover:
                return cover.link
        if len(existing_covers) > 0:
            return existing_covers[0].link
        return None

    _pandata=None
    def metadata(self):
        if not self._pandata:
            self._pandata=Pandata()
            self._pandata.load(self.yaml)
        return self._pandata.metadata

class Cover(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, db_index=True)
    link = models.URLField(max_length=500)
    default_cover = models.BooleanField(default=False)

class External_Link(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, db_index=True)
    url = models.URLField(max_length=500)
    source = models.CharField(max_length=255)