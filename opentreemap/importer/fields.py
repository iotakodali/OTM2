# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division


class species(object):
    # Fields of the OTM Species object
    GENUS = 'genus'
    SPECIES = 'species'
    CULTIVAR = 'cultivar'
    OTHER_PART_OF_NAME = 'other part of name'
    COMMON_NAME = 'common name'
    IS_NATIVE = 'is native'
    GENDER = 'gender'
    FLOWERING_PERIOD = 'flowering period'
    FRUIT_OR_NUT_PERIOD = 'fruit or nut period'
    FALL_CONSPICUOUS = 'fall conspicuous'
    FLOWER_CONSPICUOUS = 'flower conspicuous'
    PALATABLE_HUMAN = 'palatable human'
    HAS_WILDLIFE_VALUE = 'has wildlife value'
    FACT_SHEET_URL = 'fact sheet url'
    PLANT_GUIDE_URL = 'plant guide url'
    MAX_DIAMETER = 'max diameter'
    MAX_HEIGHT = 'max height'

    # Other import and/or export fields
    ID = 'database id of species'
    SCIENTIFIC_NAME = 'scientific name'
    ITREE_CODE = 'i-tree code'
    TREE_COUNT = 'number of trees in database'

    # This is a pseudo field which is filled in
    # when a matching species is found, but before
    # a commit is made. It is a list of all species
    # that somehow match this one (usda, sci name)
    POSSIBLE_MATCHES = 'calc__species'

    # This is a pseudo field which is filled in
    # when a matching itree code is found
    ITREE_PAIRS = 'calc__itree'

    DATE_FIELDS = set()

    STRING_FIELDS = {GENUS, SPECIES, CULTIVAR, OTHER_PART_OF_NAME, COMMON_NAME,
                     ITREE_CODE, GENDER, FLOWERING_PERIOD,
                     FRUIT_OR_NUT_PERIOD, FACT_SHEET_URL, PLANT_GUIDE_URL}

    POS_FLOAT_FIELDS = {MAX_DIAMETER, MAX_HEIGHT}

    FLOAT_FIELDS = set()

    POS_INT_FIELDS = set()

    BOOLEAN_FIELDS = {IS_NATIVE, FALL_CONSPICUOUS, PALATABLE_HUMAN,
                      FLOWER_CONSPICUOUS, HAS_WILDLIFE_VALUE}

    ALL = DATE_FIELDS | STRING_FIELDS | POS_FLOAT_FIELDS | \
        FLOAT_FIELDS | POS_INT_FIELDS | BOOLEAN_FIELDS

    PLOT_CHOICES = set()


class trees(object):
    # X/Y are required
    POINT_X = 'point x'
    POINT_Y = 'point y'

    # This is a pseudo field which is filled in
    # when data is cleaned and contains a GEOS
    # point object
    POINT = 'calc__point'

    # This is a pseudo field which is filled in
    # when data is cleaned and may contain a
    # OTM Species object, if the species was
    # matched
    SPECIES_OBJECT = 'calc__species_object'

    # Plot Fields
    STREET_ADDRESS = 'street address'
    CITY_ADDRESS = 'city'
    POSTAL_CODE = 'postal code'
    PLOT_WIDTH = 'plot width'
    PLOT_LENGTH = 'plot length'

    READ_ONLY = 'read only'
    OPENTREEMAP_PLOT_ID = 'opentreemap plot id'
    EXTERNAL_ID_NUMBER = 'external id number'

    TREE_PRESENT = 'tree present'

    # Tree Fields (species matching)
    GENUS = 'genus'
    SPECIES = 'species'
    CULTIVAR = 'cultivar'
    OTHER_PART_OF_NAME = 'other part of name'

    # Tree fields
    DIAMETER = 'diameter'
    TREE_HEIGHT = 'tree height'
    CANOPY_HEIGHT = 'canopy height'
    DATE_PLANTED = 'date planted'

    # order matters, so this is a tuple and not a set
    SPECIES_FIELDS = (GENUS, SPECIES, CULTIVAR, OTHER_PART_OF_NAME)

    DATE_FIELDS = {DATE_PLANTED}

    STRING_FIELDS = {STREET_ADDRESS, CITY_ADDRESS, POSTAL_CODE, GENUS,
                     SPECIES, CULTIVAR, OTHER_PART_OF_NAME, EXTERNAL_ID_NUMBER}

    POS_FLOAT_FIELDS = {PLOT_WIDTH, PLOT_LENGTH, DIAMETER, TREE_HEIGHT,
                        CANOPY_HEIGHT}

    FLOAT_FIELDS = {POINT_X, POINT_Y}

    POS_INT_FIELDS = {OPENTREEMAP_PLOT_ID}

    BOOLEAN_FIELDS = {READ_ONLY, TREE_PRESENT}

    ALL = {POINT_X, POINT_Y, PLOT_WIDTH, PLOT_LENGTH, READ_ONLY, TREE_PRESENT,
           STREET_ADDRESS, CITY_ADDRESS, POSTAL_CODE, OPENTREEMAP_PLOT_ID,
           GENUS, SPECIES, CULTIVAR, OTHER_PART_OF_NAME, DIAMETER,
           EXTERNAL_ID_NUMBER, CANOPY_HEIGHT, DATE_PLANTED, TREE_HEIGHT}
