# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import csv
import json

from celery import task
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from importer.models.base import GenericImportEvent, GenericImportRow
from importer.models.species import SpeciesImportEvent, SpeciesImportRow
from importer.models.trees import TreeImportEvent, TreeImportRow
from importer import errors
from importer.util import clean_row_data, clean_field_name

BLOCK_SIZE = 250


def _create_rows_for_event(ie, csv_file):
    # Don't use a transaction for this possibly long-running operation
    # so we can show progress. Caller does manual cleanup if necessary.
    reader = csv.DictReader(csv_file)

    field_names = reader.fieldnames
    ie.field_order = json.dumps(field_names)
    ie.save()

    field_names = [clean_field_name(f) for f in field_names]
    file_valid = ie.validate_field_names(field_names)

    if file_valid:
        _create_rows(ie, reader)

        if ie.row_count == 0:
            file_valid = False
            ie.append_error(errors.EMPTY_FILE)

    if file_valid:
        return True
    else:
        ie.status = ie.FAILED_FILE_VERIFICATION
        ie.save()
        return False


def _create_rows(ie, reader):
    RowModel = get_import_row_model(ie.import_type)
    rows = []
    idx = 0

    for row in reader:
        data = json.dumps(clean_row_data(row))
        rows.append(RowModel(data=data, import_event=ie, idx=idx))

        idx += 1
        if int(idx / BLOCK_SIZE) * BLOCK_SIZE == idx:
            RowModel.objects.bulk_create(rows)
            rows = []

    if rows:
        RowModel.objects.bulk_create(rows)  # create final partial block


@task()
def run_import_event_validation(import_type, import_event_id, file_obj):
    ie = _get_import_event(import_type, import_event_id)

    try:
        ie.status = GenericImportEvent.LOADING
        ie.save()
        success = _create_rows_for_event(ie, file_obj)
    except Exception as e:
        ie.append_error(errors.GENERIC_ERROR, data=[str(e)])
        ie.status = GenericImportEvent.FAILED_FILE_VERIFICATION
        ie.save()
        success = False

    if not success:
        try:
            ie.row_set().delete()
        except Exception:
            pass
        return

    ie.status = GenericImportEvent.VERIFIYING
    ie.save()

    for i in xrange(0, ie.row_count, BLOCK_SIZE):
        _validate_rows.delay(import_type, import_event_id, i)


@task()
def _validate_rows(import_type, import_event_id, i):
    ie = _get_import_event(import_type, import_event_id)
    for row in ie.rows()[i:(i+BLOCK_SIZE)]:
        row.validate_row()

    if _get_waiting_row_count(ie) == 0:
        ie.status = GenericImportEvent.FINISHED_VERIFICATION
        ie.save()


@task()
def commit_import_event(import_type, import_event_id):
    ie = _get_import_event(import_type, import_event_id)
    for i in xrange(0, ie.row_count, BLOCK_SIZE):
        _commit_rows.delay(import_type, import_event_id, i)


@task()
@transaction.atomic
def _commit_rows(import_type, import_event_id, i):
    ie = _get_import_event(import_type, import_event_id)

    for row in ie.rows()[i:(i + BLOCK_SIZE)]:
        row.commit_row()

    if _get_waiting_row_count(ie) == 0:
        ie.status = GenericImportEvent.FINISHED_CREATING
        ie.save()


def _get_import_event(import_type, import_event_id):
    Model = get_import_event_model(import_type)
    try:
        return Model.objects.get(pk=import_event_id)
    except ObjectDoesNotExist:
        raise Exception('Import event not found "%s" %s'
                        % (import_type, import_event_id))


def get_import_event_model(import_type):
    if import_type == SpeciesImportEvent.import_type:
        Model = SpeciesImportEvent
    elif import_type == TreeImportEvent.import_type:
        Model = TreeImportEvent
    else:
        raise Exception('Invalid import type "%s"' % import_type)
    return Model


def get_import_row_model(import_type):
    if import_type == SpeciesImportEvent.import_type:
        Model = SpeciesImportRow
    elif import_type == TreeImportEvent.import_type:
        Model = TreeImportRow
    else:
        raise Exception('Invalid import type "%s"' % import_type)
    return Model


def _get_waiting_row_count(ie):
    return ie.rows()\
             .filter(status=GenericImportRow.WAITING)\
             .count()
