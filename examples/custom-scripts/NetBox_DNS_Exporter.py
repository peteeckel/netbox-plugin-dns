#!/usr/bin/env python3

from pathlib import Path

from netbox_dns.models import View, Zone, Record

from extras.scripts import Script, StringVar, BooleanVar
from jinja2 import Environment, DictLoader


def rm_tree(path):
    for child in path.iterdir():
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)

    path.rmdir()


name = "NetBox DNS Exporters"


class ZoneExporter(Script):

    class Meta:
        name = "Zone Exporter"
        description = "This custom script can be used to export zone data to the file system"
        commit_default = True

    export_path = StringVar(
        description="Base path for the zone file export. The exporter will create a subdirectory 'netbox-dns-exporter' below this path",
        default="/home/netbox",
    )

    remove_existing_data = BooleanVar(
        description="Clean up existing data before exporting",
        default=True,
    )

    zone_template = '''\
;
; Zone file for zone {{ zone.name }} [{{ zone.view.name }}]
;

$TTL {{ zone.default_ttl }}

{% for record in records -%}
{{ record.name.ljust(32) }}    {{ (record.ttl|string if record.ttl is not none else '').ljust(8) }} IN {{ record.type.ljust(8) }}    {{ record.value }}
{% endfor %}\
'''
    jinja_env = Environment(loader=DictLoader({"zone_file": zone_template}), autoescape=False)
    template = jinja_env.get_template("zone_file")

    def run(self, data, commit):
        views = View.objects.all()

        export_path = Path(data["export_path"]) / "netbox-dns-exporter"

        if data["remove_existing_data"] and export_path.exists():
            self.log_info(f"Deleting the old export path {export_path}")
            try:
                rm_tree(export_path)
            except OSError as exc:
                self.log_failure(f"Could not remove the old export tree: {exc}")
                return

        try:
            export_path.mkdir(parents=False, exist_ok=True)
        except OSError as exc:
            self.log_failure(f"Could not create the export path {exc}")
            return

        for view in views:
            zones = Zone.objects.filter(view=view, active=True)
            if len(zones):
                self.log_info(f"Exporting zones for view '{view.name}'")
                self.export_zones(zones, view.name, export_path)

    def export_zones(self, zones, view_name, export_path):
        view_path = export_path / view_name

        try:
            view_path.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            self.log_failure(f"Could not create directory {view_path}: {exc}")
            return

        for zone in zones:
            self.log_info(f"Exporting zone {zone}")
            records = Record.objects.filter(zone=zone, active=True)

            zone_data = self.template.render({"zone": zone, "records": records})

            zone_file_path = view_path / f"{zone.name}.db"
            try:
                zone_file = open(zone_file_path, "wb")
                zone_file.write(zone_data.encode("UTF-8"))
                zone_file.close()
            except OSError as exc:
                self.log_failure(f"Could not create zone file {zone_file_path}: {exc}")
                continue
