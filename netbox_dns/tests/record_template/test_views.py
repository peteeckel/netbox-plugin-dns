from utilities.testing import ViewTestCases, create_tags

from netbox_dns.tests.custom import ModelViewTestCase
from netbox_dns.models import RecordTemplate
from netbox_dns.choices import RecordTypeChoices, RecordStatusChoices


class RecordViewTestCase(
    ModelViewTestCase,
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.GetObjectChangelogViewTestCase,
    ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkImportObjectsViewTestCase,
    ViewTestCases.BulkEditObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase,
):
    model = RecordTemplate

    @classmethod
    def setUpTestData(cls):
        cls.record_templates = (
            RecordTemplate(
                name="Record Template 1",
                type=RecordTypeChoices.CNAME,
                record_name="name1",
                value="test1.example.com",
                ttl=100,
            ),
            RecordTemplate(
                name="Record Template 2",
                type=RecordTypeChoices.A,
                record_name="name2",
                value="192.168.1.1",
                ttl=200,
            ),
            RecordTemplate(
                name="Record Template 3",
                type=RecordTypeChoices.AAAA,
                record_name="name2",
                value="fe80:dead:beef::42",
                ttl=86400,
            ),
            RecordTemplate(
                name="Record Template 4",
                type=RecordTypeChoices.TXT,
                record_name="@",
                value="Test Text",
                ttl=86400,
            ),
        )
        RecordTemplate.objects.bulk_create(cls.record_templates)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "Record Template 5",
            "type": RecordTypeChoices.AAAA,
            "record_name": "name3",
            "value": "fe80::dead:beef",
            "ttl": 86230,
            "tags": [t.pk for t in tags],
            "status": RecordStatusChoices.STATUS_ACTIVE,
        }

        cls.bulk_edit_data = {
            "record_name": "name10",
            "type": RecordTypeChoices.TXT,
            "value": "Test",
            "status": RecordStatusChoices.STATUS_INACTIVE,
            "ttl": 86420,
            "disable_ptr": True,
            "description": "New Description",
            "tag": [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,record_name,type,value,status,ttl,disable_ptr,description",
            "Record Template 7,test7,A,10.0.0.42,active,86400,false,",
            "Record Template 8,test8,AAAA,fe80:dead:beef::,active,86400,true,",
            "Record Template 9,test9,TXT,foobar,active,42300,,",
            "Record Template 10,test10,CNAME,relative.name,active,21150,,barfoo",
        )

        cls.csv_update_data = (
            "id,name,record_name,type,value,ttl,disable_ptr,description",
            f"{cls.record_templates[0].pk},New Name 1,nee1,{RecordTypeChoices.A},10.0.1.1,86442,true,foo",
            f"{cls.record_templates[1].pk},Nwr Name 2,new2,{RecordTypeChoices.AAAA},fe80:dead:beef::23,86423,false,bar",
        )

    maxDiff = None
