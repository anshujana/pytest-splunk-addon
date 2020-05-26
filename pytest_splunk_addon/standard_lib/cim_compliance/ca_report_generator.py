"""
Calculates the statistics of test cases and Creates a MarkDown Report
"""
from .markdown_report import MarkDownReport
from .markdown_table import MarkdownTable
from itertools import groupby
from collections import Counter


class CIMReportGenerator(object):
    """
    Generate the Report
    data format::

        [
                {
                    "data_model": "A",
                    "field": "aaa",
                    "data_set": "AAA",
                    "tag_stanza": "p",
                    "status": "pass"/"fail"
                }
        ]
    """

    def __init__(self, data=[], report_class=MarkDownReport):
        self.data = data
        self.report_generator = report_class()

    def add_data(self, data):
        """
        adds data to object property.

        Args:
            data(list): List of dictionaries with specified format.
        """
        self.data.append(data)

    def _group_by(self, keys, data=None):
        """
        Function to generate group of data using Keys provided

        Args:
            keys(list): Contains keys to group data by.
            data(list): list of dictionaries with specified format.
        
        Yields:
            data_set.DataSet: data set object mapped with the tags
        """
        if not data:
            data = self.data
        return groupby(data, lambda testcase: [testcase[key] for key in keys])

    def _get_count_by(self, keys, data=None):
        """
        Function to generate count of data using Keys provided

        Args:
            keys(list): Contains keys to generate count by.
            data(list): list of dictionaries with specified format.
        
        Yields:
            data_set.DataSet: data set object mapped with the tags
        """
        for grouped_by, grouped_stats in self._group_by(keys, data):
            yield (
                grouped_by,
                Counter(each["status"] for each in grouped_stats),
            )

    @staticmethod
    def pass_count(counter):
        """
        Function to Get count in Pass/Total format.

        Args:
            counter(collections.Counter): Contains counts of passing/failing Testcases.
        
        Yields:
            String: string with pass/total format.
        """
        return "{}/{}".format(
            counter["pass"], (counter["fail"] + counter["pass"])
        )

    def generate_report(self, report_path):
        """
        Function to generate report from the stored data.

        Args:
            report_path(string): Path to create the report.
        """
        self.report_generator.set_title("CIM AUDIT REPORT")
        self.data.sort(
            key=lambda tc: (
                tc["data_model"],
                tc["data_set"],
                tc["tag_stanza"],
                tc["field"],
            )
        )

        # Generating Summary table.
        self.report_generator.add_section_title("Summary Table")
        summary_table = MarkdownTable("", ["Data Model", "Pass/Total"])

        for data_model, stats in self._get_count_by(["data_model"]):
            summary_table.add_row([data_model[0], self.pass_count(stats)])

        self.report_generator.add_table(summary_table.return_table_str())

        # Generating Tag Stanza Mapping table.
        self.report_generator.add_section_title("Tag Stanza Mapping Table")
        tag_stanza_map = MarkdownTable(
            "", ["Tag Stanza", "Data Model", "Pass/Total"]
        )
        for group, stats in self._get_count_by(["data_set", "tag_stanza"]):
            data_set, tag_stanza = group
            tag_stanza_map.add_row(
                [tag_stanza, data_set, self.pass_count(stats)]
            )

        self.report_generator.add_table(tag_stanza_map.return_table_str())

        # Generating Field Summary tables.
        self.report_generator.add_section_title("Field Summary Table")

        for group_name, grouped_data in self._group_by(
            ["tag_stanza", "data_set"]
        ):
            field_summary_table = MarkdownTable(
                " - ".join(group_name), ["Field", "Status"]
            )
            for each_data in grouped_data:
                fields = False
                if each_data["field"]:
                    fields = True
                    field_summary_table.add_row(
                        [each_data["field"], each_data["status"].title()]
                    )
            if not fields:
                field_summary_table.add_row(["No", "Fields"])
            self.report_generator.add_table(
                field_summary_table.return_table_str()
            )
            del field_summary_table

        self.report_generator.write(report_path)
